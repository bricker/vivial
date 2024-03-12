// @ts-check
import { makeStyles } from "@material-ui/styles";
import classNames from "classnames";
import React, { useEffect, useState } from "react";
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
}));

const EventGlossary = () => {
  const classes = makeClasses();
  const [searchValue, setSearchValue] = useState("");
  /** @type {[Types.VirtualEvent[], React.Dispatch<React.SetStateAction<Types.VirtualEvent[]>>]} */
  const [events, setEvents] = useState([]);
  /** @type {[Types.VirtualEvent, React.Dispatch<React.SetStateAction<Types.VirtualEvent>>]} */
  const [selectedEvent, setSelectedEvent] = useState({
    name: "",
    description: "",
    fields: [],
  });
  const [isOpen, setIsOpen] = useState(false);
  const [usingMobileLayout, setUsingMobileLayout] = useState(false);

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

  // Load the events from network
  useEffect(() => {
    (async () => {
      try {
        // TODO: search/filter network req
        let e = [];
        for (let i = 0; i < 10; i++) {
          e = e.concat([
            {
              name: "account_creation",
              description:
                "lorm ipsum dolormum sode dolores huerta the bean in the baurrtiyht and then the ovsford comma gamc to save the hok intht oeth big braown hbat tath the end od rfht ehreoad",
              fields: [
                "event_descritopiton",
                "user_id",
                "visitor_id",
                "event_ts",
                "publish_time",
                "suession_id",
                "url",
                "source",
                "dvice",
                "platform",
                "content",
              ],
            },
            {
              name: "transcription_event",
              description:
                "lorm ipsum dolormum sode dolores huerta the bean in the baurrtiyht and then the ovsford comma gamc to save the hok intht oeth big braown hbat tath the end od rfht ehreoad",
              fields: [
                "event_descritopiton",
                "user_id",
                "visitor_id",
                "event_ts",
                "publish_time",
                "suession_id",
                "url",
                "source",
                "dvice",
                "platform",
                "content",
              ],
            },
            {
              name: "account_update",
              description:
                "lorm ipsum dolormum sode dolores huerta the bean in the baurrtiyht and then the ovsford comma gamc to save the hok intht oeth big braown hbat tath the end od rfht ehreoad",
              fields: [
                "event_descritopiton",
                "user_id",
                "visitor_id",
                "event_ts",
                "publish_time",
                "suession_id",
                "url",
                "source",
                "dvice",
                "platform",
                "content",
              ],
            },
            {
              name: "super_super_duper_magua_aultra_longgggggeset_long_boi_oft_them_all_this_event_is_the_best_bcus_ists_also_the_bigestestest_yes_event",
              description:
                "lorm ipsum dolormum sode dolores huerta the bean in the baurrtiyht and then the ovsforddolormum sode dolores huerta the bean in the baurrtiyht and then the ovsforddolormum sode dolores huerta the bean in the baurrtiyht and then the ovsforddolormum sode dolores huerta the bean in the baurrtiyht and then the ovsforddolormum sode dolores huerta the bean in the baurrtiyht and then the ovsforddolormum sode dolores huerta the bean in the baurrtiyht and then the ovsforddolormum sode dolores huerta the bean in the baurrtiyht and then the ovsforddolormum sode dolores huerta the bean in the baurrtiyht and then the ovsforddolormum sode dolores huerta the bean in the baurrtiyht and then the ovsforddolormum sode dolores huerta the bean in the baurrtiyht and then the ovsford comma gamc to save the hok intht oeth big braown hbat tath the end od rfht ehreoad",
              fields: [
                "event_descritopiton",
                "user_id",
                "visitor_id",
                "event_ts",
                "publish_time",
                "suession_id",
                "url",
                "source",
                "dvice",
                "platform",
                "content",
                "event_descritopiton",
                "user_id",
                "visitor_id",
                "event_ts",
                "publish_time",
                "suession_id",
                "url",
                "source",
                "dvice",
                "platform",
                "content",
                "event_descritopiton",
                "user_id",
                "visitor_id",
                "event_ts",
                "publish_time",
                "suession_id",
                "url",
                "source",
                "dvice",
                "platform",
                "content",
                "event_descritopiton",
                "user_id",
                "visitor_id",
                "event_ts",
                "publish_time",
                "suession_id",
                "url",
                "source",
                "dvice",
                "platform",
                "content",
                "event_descritopiton",
                "user_id",
                "visitor_id",
                "event_ts",
                "publish_time",
                "suession_id",
                "url",
                "source",
                "dvice",
                "platform",
                "content",
                "event_descritopiton",
                "user_id",
                "visitor_id",
                "event_ts",
                "publish_time",
                "suession_id",
                "url",
                "source",
                "dvice",
                "platform",
                "content",
                "event_descritopiton",
                "user_id",
                "visitor_id",
                "event_ts",
                "publish_time",
                "suession_id",
                "url",
                "source",
                "dvice",
                "platform",
                "content",
                "event_descritopiton",
                "user_id",
                "visitor_id",
                "event_ts",
                "publish_time",
                "suession_id",
                "url",
                "source",
                "dvice",
                "platform",
                "content",
                "event_descritopiton",
                "user_id",
                "visitor_id",
                "event_ts",
                "publish_time",
                "suession_id",
                "url",
                "source",
                "dvice",
                "platform",
                "content",
              ],
            },
          ]);
        }
        setEvents(e);
      } catch (error) {
        console.error(error);
        // TODO: set error/loading state
      }
    })();
  }, [searchValue]);

  // factored out as it's used in both the row onClick and onKeyPress actions
  function rowClicked(event) {
    setSelectedEvent(event);
    setIsOpen(true);
    // move kb focus to the sidepanel
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

        <table className={classes.table}>
          <tbody>
            <tr className={classes.tableRow}>
              <th
                className={classNames(classes.tableValue, classes.tableHeader)}
              >
                Event Name
              </th>
              <th
                className={classNames(classes.tableValue, classes.tableHeader)}
              >
                Event Description
              </th>
            </tr>
            {events.map((event) => {
              return (
                <tr
                  className={classNames(classes.tableRow, classes.rowHighlight)}
                  key={event.name}
                  tabIndex={0}
                  aria-label={`${event.name}: ${event.description}`}
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
                    {event.name}
                  </td>
                  <td className={classes.tableValue}>{event.description}</td>
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
      </div>

      {/* side panel */}
      <div id="glos_sidepanel" className={classNames(panelClasses)}>
        <button
          className={classes.closeButton}
          onClick={() => setIsOpen(false)}
        >
          <CloseIcon stroke="#363636" />
        </button>
        <h1 className={classes.panelTitle}>{selectedEvent.name}</h1>
        <p>{selectedEvent.description}</p>
        <div>
          {selectedEvent.fields.map((field) => {
            return <p key={field}>{field}</p>;
          })}
        </div>
      </div>
    </div>
  );
};

export default EventGlossary;
