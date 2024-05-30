import CloseIcon from "$eave-dashboard/js/components/Icons/CloseIcon";
import SearchIcon from "$eave-dashboard/js/components/Icons/SearchIcon";
import SidePanelIcon from "$eave-dashboard/js/components/Icons/SidePanelIcon";
import { AppContext } from "$eave-dashboard/js/context/Provider";
import useTeam from "$eave-dashboard/js/hooks/useTeam";
import { theme as eaveTheme } from "$eave-dashboard/js/theme";
import { VirtualEvent } from "$eave-dashboard/js/types.js";
import { CircularProgress } from "@mui/material";
import classNames from "classnames";
import React, { useCallback, useContext, useEffect, useState } from "react";
import { makeStyles } from "tss-react/mui";

const makeClasses = makeStyles<void, "hoverIcon">()(
  (theme, _params, classes) => ({
    glossary: {
      padding: "10px 24px",
      overflowY: "scroll",
      flexGrow: 1,
    },
    header: {
      fontSize: 34,
      fontWeight: 400,
    },
    searchBar: {
      maxWidth: 789,
      minWidth: "calc(100vw / 2)",
      display: "flex",
      flexDirection: "row",
      alignItems: "center",
      textAlign: "center",
      borderRadius: 20,
      backgroundColor: "#f1f1f1",
      boxSizing: "border-box",
      padding: 12,
      marginTop: 18,
      "&:focus-within": {
        outline: "2px solid",
      },
      header: {
        fontSize: 34,
        fontWeight: 400,
      },
      searchBar: {
        maxWidth: 789,
        minWidth: "calc(100vw / 2)",
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        textAlign: "center",
        borderRadius: 20,
        backgroundColor: "#f1f1f1",
        boxSizing: "border-box",
        padding: 12,
        marginTop: 18,
        "&:focus-within": {
          outline: "2px solid",
        },
      },
      searchIcon: {
        position: "relative",
        top: 3,
      },
      searchInput: {
        backgroundColor: "transparent",
        outline: "none",
        fontSize: 16,
        padding: "1px 10px",
        border: "none",
        flexGrow: 1,
      },
      table: {
        borderCollapse: "collapse",
        width: "100%",
        maxWidth: 1000,
        fontSize: 14,
        marginTop: 60,
      },
      tableValue: {
        textAlign: "left",
        padding: "12px 24px",
      },
      columnWidthLimit: {
        maxWidth: "calc(100vw / 3)",
      },
      tableHeader: {
        fontWeight: "bold",
        fontSize: 16,
      },
      tableRow: {
        "&:nth-child(even)": {
          backgroundColor: "#e5e9f5",
        },
      },
      rowHighlight: {
        "&:hover": {
          backgroundColor: "#36363666",
          cursor: "pointer",
        },
        [`&:hover ${classes.hoverIcon}`]: {
          opacity: 100,
        },
      },
      hoverIcon: {
        opacity: 0,
      },
      root: {
        display: "flex",
        flexDirection: "row",
        flexGrow: 1,
        wordWrap: "break-word",
        overflowX: "hidden",
      },
      panelContainer: {
        position: "fixed",
        right: 0,
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        height: "100vh",
        width: "calc(100vw / 4)",
        backgroundColor: "#e5e9f5",
      },
    },
    rowHighlight: {
      "&:hover": {
        backgroundColor: "#36363666",
        cursor: "pointer",
      },
      [`&:hover ${classes.hoverIcon}`]: {
        opacity: 100,
      },
    },
    hoverIcon: {
      opacity: 0,
    },
    root: {
      display: "flex",
      flexDirection: "row",
      flexGrow: 1,
      wordWrap: "break-word",
      overflowX: "hidden",
    },
    panelContainer: {
      position: "fixed",
      right: 0,
      display: "flex",
      flexDirection: "column",
      alignItems: "flex-start",
      height: "100vh",
      width: "calc(100vw / 4)",
      backgroundColor: "#e5e9f5",
      padding: 24,
      overflow: "auto",
    },
    panelHidden: {
      left: "100%",
    },
    panelFullScreen: {
      width: "100%",
    },
    closeButton: {
      alignSelf: "flex-end",
      cursor: "pointer",
      border: "none",
      backgroundColor: "transparent",
    },
    panelTitle: {
      // prevent long event names from stretching out of bounds
      wordWrap: "break-word",
      maxWidth: "80vw",
      [theme.breakpoints.up("md")]: {
        maxWidth: "calc(100vw / 5)",
      },
    },
    loader: {
      display: "flex",
      width: "100%",
      alignItems: "center",
      justifyContent: "center",
      marginTop: 32,
    },
    noEventsHeader: {
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
    },
    error: {
      color: theme.palette.error.main,
      padding: "0px 30px",
      textAlign: "center",
      fontSize: "26px",
    },
  }),
);

const Glossary = () => {
  const { classes } = makeClasses();
  const [searchValue, setSearchValue] = useState("");
  const [selectedEvent, setSelectedEvent] = useState<VirtualEvent | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [usingMobileLayout, setUsingMobileLayout] = useState(false);
  const { team, getTeamVirtualEvents } = useTeam();

  const { glossaryNetworkStateCtx } = useContext(AppContext);
  const [networkState] = glossaryNetworkStateCtx!;

  // initial data load
  useEffect(() => {
    getTeamVirtualEvents(null);
  }, []);

  useEffect(() => {
    const handleResize = () => {
      setUsingMobileLayout(
        window.innerWidth <= eaveTheme.breakpoints.values.md,
      );
    };

    handleResize();

    // Add event listener for window resize
    window.addEventListener("resize", handleResize);
    // Remove event listener on component unmount
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  const panelClasses = [classes.panelContainer];
  const glossaryClasses = [classes.glossary];
  if (!isOpen) {
    panelClasses.push(classes.panelHidden);
  } else if (usingMobileLayout) {
    panelClasses.push(classes.panelFullScreen);
  }

  // useCallback to preserve timer variable across renders
  const debouncedFilterEventsOnType = useCallback(
    (() => {
      const halfSecondMs = 500;
      let timer: NodeJS.Timeout | undefined = undefined;

      return (searchTerm: string) => {
        clearTimeout(timer);
        timer = setTimeout(() => {
          if (!searchTerm) {
            // refresh results w/ all events when search bar is emptied
            getTeamVirtualEvents(null);
            return;
          }
          if (searchTerm.length < 3) {
            // wait for min 3 chars to be typed before doing a search
            return;
          }
          getTeamVirtualEvents({ search_term: searchTerm });
        }, halfSecondMs);
      };
    })(),
    [],
  );

  // perform search for events
  useEffect(() => {
    debouncedFilterEventsOnType(searchValue);
  }, [searchValue]);

  // factored out as it's used in both the row onClick and onKeyPress actions
  const rowClicked = (event: VirtualEvent) => {
    setSelectedEvent(event);
    setIsOpen(true);
    // move kb focus to the sidepanel for a11y
    const sidepanel = document.getElementById("glos_sidepanel");
    sidepanel?.focus();
  };

  let component: React.ReactElement;

  if (team?.virtualEvents?.length) {
    // show the virtual events table
    component = (
      <table className={classes.table}>
        <tbody>
          <tr className={classes.tableRow}>
            <th className={classNames(classes.tableValue, classes.tableHeader)}>
              Event Name
            </th>
            <th className={classNames(classes.tableValue, classes.tableHeader)}>
              Event Description
            </th>
          </tr>
          {team.virtualEvents.map((event) => (
            <tr
              className={classNames(classes.tableRow, classes.rowHighlight)}
              key={event.readable_name}
              tabIndex={0}
              aria-label={`${event.readable_name}: ${event.description}`}
              role="button"
              onClick={() => rowClicked(event)}
              onKeyDown={(pressed) => {
                if (pressed.key === "Enter" || pressed.key === " ") {
                  rowClicked(event);
                }
              }}
            >
              <td
                className={classNames(
                  classes.tableValue,
                  classes.columnWidthLimit,
                )}
              >
                {event.readable_name}
              </td>
              <td className={classes.tableValue}>{event.description}</td>
              <td>
                <span
                  className={classNames(classes.hoverIcon, classes.tableValue)}
                >
                  <SidePanelIcon color="#363636" />
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  } else if (networkState.virtualEventsAreLoading) {
    // show loading state
    component = (
      <div className={classes.loader}>
        <CircularProgress color="secondary" />
      </div>
    );
  } else if (networkState.virtualEventsAreErroring) {
    // show err state
    component = (
      <div className={classes.error}>
        ERROR: Unable to fetch virtual events{" "}
        {searchValue ? `for searched term "${searchValue}"` : ""}
      </div>
    );
  } else {
    // not loading/erroring and no events found
    component = (
      <div className={classes.noEventsHeader}>
        <h2>No virtual events found</h2>
      </div>
    );
  }

  let sidepanelContent: React.ReactElement;

  if (selectedEvent) {
    sidepanelContent = (
      <>
        <h1 className={classes.panelTitle}>{selectedEvent.readable_name}</h1>
        <p>{selectedEvent.description}</p>
        <div>
          TODO add fields column to VirtualEventOrm
          {/* {selectedEvent.fields.map((field) => {
          return <p key={field}>{field}</p>;
        })} */}
        </div>
      </>
    );
  } else {
    sidepanelContent = <p>Select an event to see details.</p>;
  }

  return (
    <>
      <div className={classes.root}>
        <div className={classNames(glossaryClasses)}>
          <h1 className={classes.header}>Event Glossary</h1>

          <div className={classes.searchBar}>
            <i className={classes.searchIcon}>
              <SearchIcon color="#33363f" />
            </i>
            <input
              type="text"
              className={classes.searchInput}
              placeholder="Type to search events"
              value={searchValue}
              onChange={(elem) => setSearchValue(elem.target.value)}
            />
          </div>

          {component}
        </div>
      </div>
      {/* side panel */}
      <div id="glos_sidepanel" className={classNames(panelClasses)}>
        <button
          className={classes.closeButton}
          onClick={() => setIsOpen(false)}
        >
          <CloseIcon stroke="#363636" />
        </button>
        {sidepanelContent}
      </div>
    </>
  );
};

export default Glossary;
