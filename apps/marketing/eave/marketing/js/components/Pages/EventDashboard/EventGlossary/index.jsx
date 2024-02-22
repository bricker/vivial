// @ts-check
import { makeStyles } from "@material-ui/styles";
import classNames from "classnames";
import React, { useEffect, useState } from "react";
import * as Types from "../../../../types.js"; // eslint-disable-line no-unused-vars
import SearchIcon from "../../../Icons/SearchIcon.jsx";
import SidePanelIcon from "../../../Icons/SidePanelIcon.jsx";
import CloseIcon from "../../../Icons/CloseIcon.js";


const width = 420;
const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
  glossary: {
    padding: "10px 24px",
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
  },
  searchIcon: {
    position: "relative",
    top: 3,
  },
  searchInput: {
    backgroundColor: "transparent",
    fontSize: 16,
    padding: "1px 10px",
    outline: "none",
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
    overflow: 'hidden',
    gap: 0,
  },
  panelContainer: {
    height: "100vh",
    width: width, //'100% / 3',
    backgroundColor: "#e5e9f5",
    transition: "1s cubic-bezier(.36,-0.01,0,.77)",
    padding: 16,
  },
  panelHidden: {
    marginRight: -width,
  },
  closeButton: {
    float: "right",
  },
}));

// TODO: sidepanel + a11y
const EventGlossary = () => {
  const classes = makeClasses();
  const [searchValue, setSearchValue] = useState("");
  /** @type {[Types.VirtualEvent[], React.Dispatch<React.SetStateAction<Types.VirtualEvent[]>>]} */
  const [events, setEvents] = useState([]);
  /** @type {[Types.VirtualEvent, React.Dispatch<React.SetStateAction<Types.VirtualEvent>>]} */
  const [selectedEvent, setSelectedEvent] = useState({
    name: '',
    description: '',
    fields: [],
  });
  const [isOpen, setIsOpen] = useState(false);

  const classList = [classes.panelContainer];
  if (!isOpen) {
    classList.push(classes.panelHidden);
  }
  const panelClasses = classNames(classList);


  useEffect(() => {
    (async () => {
      try {
        // TODO: search/filter network req
        setEvents([
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
        ]);
      } catch (error) {
        console.error(error);
        // TODO: set error/loading state
      }
    })();
  }, [searchValue]);

  return (
    <div className={classes.root}>
      <div className={classes.glossary}>
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
                  onClick={() => {
                    setSelectedEvent(event);
                    setIsOpen(true);
                  }}
                >
                  <td className={classes.tableValue}>{event.name}</td>
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
      <div className={panelClasses}>
        <button
          className={classes.closeButton}
          onClick={() => setIsOpen(false)}
        >
          <CloseIcon stroke="#363636" />
        </button>
        <h1>{selectedEvent.name}</h1>
        <p>{selectedEvent.description}</p>
        {selectedEvent.fields.map((field) => {
          return <p key={field}>{field}</p>;
        })}
      </div>
    </div>
  );
};

export default EventGlossary;
