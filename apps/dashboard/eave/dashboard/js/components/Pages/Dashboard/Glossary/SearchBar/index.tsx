import SearchIcon from "$eave-dashboard/js/components/Icons/SearchIcon";
import useTeam from "$eave-dashboard/js/hooks/useTeam";
import React, { useCallback, useEffect, useState } from "react";
import { makeStyles } from "tss-react/mui";

const makeClasses = makeStyles()((_theme, _params, _classes) => ({
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
}));

const SearchBar = () => {
  const { classes } = makeClasses();
  const [searchValue, setSearchValue] = useState("");
  const { getTeamVirtualEvents } = useTeam();

  // useCallback to preserve timer variable across renders
  const debouncedFilterEventsOnType = useCallback(
    (() => {
      const halfSecondMs = 500;
      let timer: number | undefined = undefined;

      return (searchTerm: string) => {
        window.clearTimeout(timer);
        timer = window.setTimeout(() => {
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

  return (
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
  );
};

export default SearchBar;
