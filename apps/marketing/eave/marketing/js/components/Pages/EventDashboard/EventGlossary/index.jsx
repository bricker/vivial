// @ts-check
import { makeStyles } from "@material-ui/styles";
import classNames from "classnames";
import React, { useEffect, useState } from "react";
import * as Types from "../../../../types.js"; // eslint-disable-line no-unused-vars
import SearchIcon from "../../../Icons/SearchIcon.jsx";
import SidePanelIcon from "../../../Icons/SidePanelIcon.jsx";

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
  root: {
    padding: "24px 30px",
  },
  header: {
    fontSize: 32,
  },
  searchBar: {
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    textAlign: "center",
    borderRadius: 20,
    backgroundColor: "#f1f1f1",
    boxSizing: "border-box",
    padding: 12,
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
}));

// TODO: sidepanel
const EventGlossary = () => {
  const classes = makeClasses();
  const [searchValue, setSearchValue] = useState("");
  // const [events, setEvents] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        // TODO: search/filter network req
        // setEvents();
      } catch (error) {
        console.error(error);
        // TODO: set error state
      }
    })();
  }, [searchValue]);

  // TODO: network request
  const events = [
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
  ];

  return (
    <div className={classes.root}>
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
            <th className={classNames(classes.tableValue, classes.tableHeader)}>
              Event Name
            </th>
            <th className={classNames(classes.tableValue, classes.tableHeader)}>
              Event Description
            </th>
          </tr>
          {events.map((event) => {
            return (
              <tr
                className={classNames(classes.tableRow, classes.rowHighlight)}
                key={event.name}
              >
                <td className={classes.tableValue}>{event.name}</td>
                <td className={classes.tableValue}>{event.description}</td>
                <td>
                  <span className={classNames(classes.hoverIcon, classes.tableValue)}>
                    <SidePanelIcon color="#363636" />
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default EventGlossary;
