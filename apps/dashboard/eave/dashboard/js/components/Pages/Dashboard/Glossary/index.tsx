import CloseIcon from "$eave-dashboard/js/components/Icons/CloseIcon";
import SidePanelIcon from "$eave-dashboard/js/components/Icons/SidePanelIcon";
import SearchBar from "$eave-dashboard/js/components/Pages/Dashboard/Glossary/SearchBar";
import { AppContext } from "$eave-dashboard/js/context/Provider";
import {
  closePanel,
  listVirtualEvents,
  selectEvent,
  selectGlossary,
  selectVirtualEvents,
  setUsingMobileLayout,
} from "$eave-dashboard/js/features/eventIndex/eventIndexSlice";
import useTeam from "$eave-dashboard/js/hooks/useTeam";
import { AppDispatch } from "$eave-dashboard/js/store";
import { theme as eaveTheme } from "$eave-dashboard/js/theme";
import { VirtualEventDetails, VirtualEventField } from "$eave-dashboard/js/types";
import { CircularProgress } from "@mui/material";
import classNames from "classnames";
import React, { useContext, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { makeStyles } from "tss-react/mui";

const makeClasses = makeStyles<void, "hoverIcon">()((theme, _params, classes) => ({
  glossary: {
    padding: "10px 24px",
    overflowY: "scroll",
    flexGrow: 1,
  },
  header: {
    fontSize: 34,
    fontWeight: 400,
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
  fieldContainer: {
    margin: 2,
    marginLeft: 10,
    padding: 6,
    border: "2px solid gray",
    borderRadius: 5,
  },
}));

const Glossary = () => {
  const { classes } = makeClasses();

  const dispatch: AppDispatch = useDispatch();
  const { selectedEvent, isOpen, usingMobileLayout } = useSelector(selectGlossary);

  const virtualEvents = useSelector(selectVirtualEvents);

  const { team, getVirtualEventDetails } = useTeam();

  const { glossaryNetworkStateCtx } = useContext(AppContext);
  const [networkState] = glossaryNetworkStateCtx!;

  // initial data load
  useEffect(() => {
    dispatch(listVirtualEvents({ query: null }));
  }, [dispatch]);

  // load up event details when a new one is selected
  useEffect(() => {
    if (selectedEvent) {
      console.log("CLICKED");
      getVirtualEventDetails(selectedEvent.id);
    }
  }, [dispatch, selectedEvent]);

  useEffect(() => {
    const handleResize = () => {
      dispatch(setUsingMobileLayout(window.innerWidth <= eaveTheme.breakpoints.values.md));
    };

    handleResize();

    // Add event listener for window resize
    window.addEventListener("resize", handleResize);
    // Remove event listener on component unmount
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [dispatch]);

  const panelClasses = [classes.panelContainer];
  const glossaryClasses = [classes.glossary];
  if (!isOpen) {
    panelClasses.push(classes.panelHidden);
  } else if (usingMobileLayout) {
    panelClasses.push(classes.panelFullScreen);
  }

  // factored out as it's used in both the row onClick and onKeyPress actions
  const rowClicked = (event: VirtualEventDetails) => {
    dispatch(selectEvent(event));
    // move kb focus to the sidepanel for a11y
    const sidepanel = document.getElementById("glos_sidepanel");
    sidepanel?.focus();
  };

  let component: React.ReactElement;

  if (virtualEvents?.length) {
    // show the virtual events table
    component = (
      <table className={classes.table}>
        <tbody>
          <tr className={classes.tableRow}>
            <th className={classNames(classes.tableValue, classes.tableHeader)}>Event Name</th>
            <th className={classNames(classes.tableValue, classes.tableHeader)}>Event Description</th>
          </tr>
          {virtualEvents.map((event) => (
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
              <td className={classNames(classes.tableValue, classes.columnWidthLimit)}>{event.readable_name}</td>
              <td className={classes.tableValue}>{event.description}</td>
              <td>
                <span className={classNames(classes.hoverIcon, classes.tableValue)}>
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
    component = <div className={classes.error}>ERROR: Unable to fetch virtual events</div>;
  } else {
    // not loading/erroring and no events found
    component = (
      <div className={classes.noEventsHeader}>
        <h2>No virtual events found</h2>
      </div>
    );
  }

  let sidepanelContent: React.ReactElement;

  function fieldGenerator(fields: VirtualEventField[] | null | undefined): React.ReactElement[] | null {
    if (!fields) {
      return null;
    }
    return fields.map((field) => (
      <div key={field.name} className={classes.fieldContainer}>
        <h4>{field.name}</h4>
        <p>
          {field.field_type} ({field.mode})
        </p>
        <p>{field.description || "(No description)"}</p>
        {fieldGenerator(field.fields)}
      </div>
    ));
  }

  if (selectedEvent) {
    // selectedEvent can become stale, as it is a copy of the element in team.virtualEvents,
    // not a direct reference. When details are finished loading and the event that
    // selectedEvent copied is updated, selectedEvent remains with empty fields.
    const freshEvent = team?.virtualEvents?.find((e) => e.id === selectedEvent.id);
    sidepanelContent = (
      <>
        <h1 className={classes.panelTitle}>{selectedEvent.readable_name}</h1>
        <p>{selectedEvent.description}</p>
        {freshEvent?.fields?.length ? (
          // left -10 to counter record nesting indent for the first layer
          <div style={{ marginLeft: -10 }}>{fieldGenerator(freshEvent.fields)}</div>
        ) : networkState.virtualEventsAreLoading ? (
          <div className={classes.loader}>
            <CircularProgress color="secondary" />
          </div>
        ) : networkState.virtualEventsAreErroring ? (
          <div className={classes.error}>ERROR: Unable to fetch virtual event details</div>
        ) : (
          <p>No field details</p>
        )}
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

          <SearchBar />

          {component}
        </div>
      </div>
      {/* side panel */}
      <div id="glos_sidepanel" className={classNames(panelClasses)}>
        <button className={classes.closeButton} onClick={() => dispatch(closePanel())}>
          <CloseIcon stroke="#363636" />
        </button>
        {sidepanelContent}
      </div>
    </>
  );
};

export default Glossary;
