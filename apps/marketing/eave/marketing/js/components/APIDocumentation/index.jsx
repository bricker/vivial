import { CircularProgress, Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import React, { useEffect } from "react";
import { DOC_STATUSES } from "../../constants.js";
import useTeam from "../../hooks/useTeam";

const makeClasses = makeStyles((theme) => ({
  container: {
    color: theme.palette.background.contrastText,
    padding: "0 25px",
    marginBottom: 80,
    [theme.breakpoints.up("md")]: {
      padding: "0 128px",
    },
  },
  title: {
    color: theme.palette.tertiary.main,
    fontSize: 32,
    fontWeight: 400,
    marginBottom: 22,
    [theme.breakpoints.up("md")]: {
      fontSize: 36,
      marginBottom: 28,
    },
  },
  loader: {
    color: theme.palette.tertiary.main,
    textAlign: "center",
  },
  docTable: {
    width: "100%",
    borderCollapse: "collapse",
  },
  docTableLabel: {
    paddingBottom: 16,
    fontSize: 20,
    fontWeight: 400,
    textAlign: "left",
  },
  docTableBody: {
    fontSize: 16,
  },
  docTableData: {
    padding: "18px 0",
  },
  docTableRow: {
    borderBottom: `1px solid ${theme.palette.background.contrastText}`,
  },
}));

function formatStatus(doc) {
  const status = doc.status;
  const pullRequestNumber = doc.pull_request_number;

  // Example PR Link: https://github.com/eave-fyi/eave-monorepo/pull/163
  // Missing: org, repo name

  switch (status) {
    case DOC_STATUSES.PROCESSING:
      return "Processing";
    case DOC_STATUSES.PR_OPENED:
      return "PR Created";
    case DOC_STATUSES.PR_MERGED:
      return "PR Merged";
    default:
      return "-";
  }
}

function formatLastUpdated(doc) {
  return doc.status_updated;
}

function renderContent(classes, team) {
  const { apiDocsErroring, apiDocsLoading, apiDocsFetchCount, apiDocs } = team;
  if (apiDocsErroring) {
    return (
      <Typography color="error" variant="h6">
        ERROR: Unable to fetch API documentation.
      </Typography>
    );
  }
  if (apiDocsFetchCount === 0 && apiDocsLoading) {
    return (
      <div className={classes.loader}>
        <CircularProgress color="inherit" />
      </div>
    );
  }
  if (apiDocs.length === 0) {
    return (
      <Typography color="inherit" variant="h6">
        Eave is currently searching for Express APIs within your repositories.
        This may take some time. Please check back for any documentation
        created.
      </Typography>
    );
  }
  return (
    <table className={classes.docTable}>
      <thead className={classes.docTableHeader}>
        <tr className={classes.docTableRow}>
          <th className={classes.docTableLabel}>Name</th>
          <th className={classes.docTableLabel}>Status</th>
          <th className={classes.docTableLabel}>Last Updated</th>
        </tr>
      </thead>
      <tbody className={classes.docTableBody}>
        {apiDocs.map((doc) => (
          <tr key={doc.id} className={classes.docTableRow}>
            <td className={classes.docTableData}>{doc.api_name}</td>
            <td className={classes.docTableData}>{formatStatus(doc)}</td>
            <td className={classes.docTableData}>{formatLastUpdated(doc)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

const APIDocumentation = () => {
  const { team, getTeamAPIDocs } = useTeam();
  const classes = makeClasses();

  useEffect(() => {
    getTeamAPIDocs();
    // const interval = setInterval(getTeamAPIDocs, 8000);
    // return () => clearInterval(interval);
  }, []);

  return (
    <section className={classes.container}>
      <Typography className={classes.title} variant="h2">
        API Documentation
      </Typography>
      {renderContent(classes, team)}
    </section>
  );
};

export default APIDocumentation;
