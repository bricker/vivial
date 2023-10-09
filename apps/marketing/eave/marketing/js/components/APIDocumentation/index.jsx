import React, { useEffect, useState } from "react";
import { CircularProgress } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { Typography } from "@material-ui/core";
import useTeam from "../../hooks/useTeam";
import { mapReposByExternalId } from "../../util/repo-util.js";
import { DOC_STATUSES, MONTH_NAMES } from "../../constants.js";

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
    width: '100%',
    borderCollapse: 'collapse',
  },
  docTableLabel: {
    paddingBottom: 16,
    fontSize: 20,
    fontWeight: 400,
    textAlign: 'left',
    '&:first-of-type': {
      paddingLeft: 8,
    }
  },
  docTableBody: {
    fontSize: 16,
  },
  docTableData: {
    padding: '18px 0',
  },
  docNameData: {
    padding: '18px 8px',
    fontWeight: 700,
  },
  docTableRow: {
    borderBottom: `1px solid ${theme.palette.background.contrastText}`,
  },
  compactDocView: {
    borderTop: `1px solid ${theme.palette.background.contrastText}`,
  },
  compactDocRow: {
    borderBottom: `1px solid ${theme.palette.background.contrastText}`,
    padding: '14px 5px',
    fontSize: 16,
  },
  compactDocName: {
    fontWeight: 700,
  }
}));

function formatStatus(doc, repoMap) {
  const status = doc.status;
  if (status === DOC_STATUSES.PROCESSING) {
    return "Processing";
  }

  const repo = repoMap[doc.external_repo_id];
  const repoUrl = repo.external_repo_data.url;
  const prNumber = doc.pull_request_number;
  const prLink = `${repoUrl}/pull/${prNumber}`;
  const prLinkStyle = {'color': '#0092C7', textDecoration: 'none'};
  const prStatus = (status === DOC_STATUSES.PR_OPENED) ? "PR Created" : "PR Merged";

  return <>{prStatus} (<a target="_blank" href={prLink} style={prLinkStyle}>#{prNumber}</a>)</>;
}

function formatLastUpdated(doc) {
  if (!doc.status_updated) {
    return "-";
  }
  const updatedDate = new Date(doc.status_updated);
  const today = new Date();
  if (updatedDate.toDateString() === today.toDateString()) {
    return "Today";
  }
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  if (updatedDate.toDateString() === yesterday.toDateString()) {
    return "Yesterday";
  }
  const month = MONTH_NAMES[updatedDate.getMonth()];
  const day = updatedDate.getDate();
  const year = updatedDate.getFullYear();
  return `${month} ${day}, ${year}`;
}

function renderContent(classes, team, compact) {
  const {apiDocsErroring, apiDocsLoading, apiDocsFetchCount, apiDocs, repos } = team;
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
        Eave is currently searching for Express APIs within your repositories. This may take some time. Please check back for any documentation created.
      </Typography>
    );
  }
  const repoMap = mapReposByExternalId(repos);
  const handleRowClick = (e, doc) => {
    const filePath = doc.file_path;
    const isProcessing = doc.status === DOC_STATUSES.PROCESSING;
    const isLink = e.target.tagName === "A"
    if (filePath && !isProcessing && !isLink) {
      const repo = repoMap[doc.external_repo_id];
      const repoUrl = repo.external_repo_data.url;
      window.open(`${repoUrl}/${filePath}`);
    }
  };
  const handleRowMouseOver = (e, doc) => {
    const filePath = doc.file_path;
    const isProcessing = doc.status === DOC_STATUSES.PROCESSING;
    if (filePath && !isProcessing) {
      const tr = e.target.closest('tr');
      tr.style.setProperty('background-color', "#3E3E3E");
    }
  };
  const handleRowMouseOut = (e, doc) => {
    const tr = e.target.closest('tr');
    tr.style.removeProperty('background-color');
  };

  if (compact) {
    return (
      <div className={classes.compactDocView}>
        {apiDocs.map((doc) => (
          <div
            key={doc.id}
            className={classes.compactDocRow}
            onDoubleClick={(e) => handleRowClick(e, doc)}
          >
            <div className={classes.compactDocName}>{doc.api_name}</div>
            <div>Status: {formatStatus(doc, repoMap)}</div>
            <div>Last Updated: {formatLastUpdated(doc)}</div>
          </div>
        ))}
      </div>
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
          <tr
            key={doc.id}
            className={classes.docTableRow}
            onDoubleClick={(e) => handleRowClick(e, doc)}
            onMouseOver={(e) => handleRowMouseOver(e, doc)}
            onMouseOut={(e) => handleRowMouseOut(e, doc)}
          >
            <td className={classes.docNameData}>{doc.api_name}</td>
            <td className={classes.docTableData}>{formatStatus(doc, repoMap)}</td>
            <td className={classes.docTableData}>{formatLastUpdated(doc)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

const APIDocumentation = () => {
  const { team, getTeamAPIDocs } = useTeam();
  const [compact, setCompact] = useState(window.innerWidth < 900);
  const classes = makeClasses();

  useEffect(() => {
    getTeamAPIDocs();
    const interval = setInterval(getTeamAPIDocs, 8000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleResize = () => setCompact(window.innerWidth < 900);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <section className={classes.container}>
      <Typography className={classes.title} variant="h2">
        API Documentation
      </Typography>
      {renderContent(classes, team, compact)}
    </section>
  );
};

export default APIDocumentation;
