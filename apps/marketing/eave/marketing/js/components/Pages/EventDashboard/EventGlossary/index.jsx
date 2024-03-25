// @ts-check
import { CircularProgress } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import classNames from "classnames";
import React, { useContext, useEffect, useState } from "react";
import { AppContext } from "../../../../context/Provider.js";
import useTeam from "../../../../hooks/useTeam.js";
import { theme } from "../../../../theme.js";
import * as Types from "../../../../types.js"; // eslint-disable-line no-unused-vars
import CloseIcon from "../../../Icons/CloseIcon.js";
import SearchIcon from "../../../Icons/SearchIcon.jsx";
import SidePanelIcon from "../../../Icons/SidePanelIcon.jsx";

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
  glossary: {
    padding: "10px 24px",
    overflowY: "scroll",
    flex: 3,
  },
  header: {
    fontSize: 34,
    fontWeight: 400,
  },
  searchBar: {
    maxWidth: 789,
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
    "&:hover $hoverIcon": {
      opacity: 100,
    },
  },
  hoverIcon: {
    opacity: 0,
  },
  root: {
    display: "flex",
    flexDirection: "row",
    wordWrap: "break-word",
    overflowX: "hidden",
  },
  panelContainer: {
    position: "sticky",
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-start",
    height: "100vh",
    maxWidth: "100vw / 4",
    backgroundColor: "#e5e9f5",
    [theme.breakpoints.up("md")]: {
      transition: "1s cubic-bezier(.36,-0.01,0,.77)",
    },
    padding: 24,
    overflow: "auto",
    flex: 1,
  },
  panelHidden: {
    flex: 0,
    padding: 0, // any padding keeps the panel visible
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
    // @ts-ignore
    color: theme.palette.background.contrastText,
    width: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
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
}));

const EventGlossary = () => {
  const classes = makeClasses();
  const [searchValue, setSearchValue] = useState("");
  /** @type {[Types.VirtualEvent, React.Dispatch<React.SetStateAction<Types.VirtualEvent>>]} */
  const [selectedEvent, setSelectedEvent] = useState({
    id: "",
    readable_name: "",
    description: "",
    fields: [],
  });
  const [isOpen, setIsOpen] = useState(false);
  const [usingMobileLayout, setUsingMobileLayout] = useState(false);
  const { team, getTeamVirtualEvents } = useTeam();
  const {
    glossaryNetworkStateCtx: [networkState],
  } = useContext(AppContext);

  // initial data load
  useEffect(() => {
    getTeamVirtualEvents(null);
  }, []);

  useEffect(() => {
    const handleResize = () => {
      setUsingMobileLayout(window.innerWidth <= theme.breakpoints.values.md);
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
    glossaryClasses.push(classes.panelHidden);
  }

  // perform search for events
  useEffect(() => {
    setIsOpen(false);
    getTeamVirtualEvents(searchValue ? { search_term: searchValue } : null);
  }, [searchValue]);

  // factored out as it's used in both the row onClick and onKeyPress actions
  function rowClicked(event) {
    setSelectedEvent(event);
    setIsOpen(true);
    // move kb focus to the sidepanel for a11y
    const sidepanel = document.getElementById("glos_sidepanel");
    sidepanel?.focus();
  }

  return (
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

        {(() => {
          // show loading state
          if (networkState.virtualEventsAreLoading) {
            return (
              <div className={classes.loader}>
                <CircularProgress color="inherit" />
              </div>
            );
          }
          // show err state
          if (networkState.virtualEventsAreErroring) {
            return (
              <div className={classes.error}>
                ERROR: Unable to fetch virtual events{" "}
                {searchValue ? `for searched term "${searchValue}"` : ""}
              </div>
            );
          }
          if (team?.virtualEvents) {
            // show the virtual events table
            return (
              <table className={classes.table}>
                <tbody>
                  <tr className={classes.tableRow}>
                    <th
                      className={classNames(
                        classes.tableValue,
                        classes.tableHeader,
                      )}
                    >
                      Event Name
                    </th>
                    <th
                      className={classNames(
                        classes.tableValue,
                        classes.tableHeader,
                      )}
                    >
                      Event Description
                    </th>
                  </tr>
                  {team.virtualEvents.map((event) => {
                    return (
                      <tr
                        className={classNames(
                          classes.tableRow,
                          classes.rowHighlight,
                        )}
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
                        <td className={classes.tableValue}>
                          {event.description}
                        </td>
                        <td>
                          <span
                            className={classNames(
                              classes.hoverIcon,
                              classes.tableValue,
                            )}
                          >
                            <SidePanelIcon color="#363636" />
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            );
          } else {
            // not loading/erroring and no events found
            return (
              <div className={classes.noEventsHeader}>
                <h2>No virtual events found</h2>
              </div>
            );
          }
        })()}
      </div>

      {/* side panel */}
      <div id="glos_sidepanel" className={classNames(panelClasses)}>
        <button
          className={classes.closeButton}
          onClick={() => setIsOpen(false)}
        >
          <CloseIcon stroke="#363636" />
        </button>
        <h1 className={classes.panelTitle}>{selectedEvent.readable_name}</h1>
        <p>{selectedEvent.description}</p>
        <div>
          {selectedEvent.fields?.map((field) => {
            return <p key={field}>{field}</p>;
          })}
        </div>
      </div>
    </div>
  );
};

export default EventGlossary;
