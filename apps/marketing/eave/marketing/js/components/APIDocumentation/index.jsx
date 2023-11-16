// @ts-check
import { CircularProgress, Link, Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import React, { useEffect, useState } from "react";
import useTeam from "../../hooks/useTeam";
import * as Types from "../../types.js"; // eslint-disable-line no-unused-vars
import { mapReposById } from "../../util/repo-util.js";

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
  container: {
    // @ts-ignore
    color: theme.palette.background.contrastText,
    padding: "0 25px",
    marginBottom: 80,
    [theme.breakpoints.up("md")]: {
      padding: "0 128px",
    },
  },
  title: {
    // @ts-ignore
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
    // @ts-ignore
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
    "&:first-of-type": {
      paddingLeft: 8,
    },
  },
  docTableBody: {
    fontSize: 16,
  },
  docTableData: {
    padding: "18px 0",
  },
  docNameData: {
    padding: "18px 8px",
    fontWeight: 700,
  },
  docTableRow: {
    // @ts-ignore
    borderBottom: `1px solid ${theme.palette.background.contrastText}`,
  },
  compactDocView: {
    // @ts-ignore
    borderTop: `1px solid ${theme.palette.background.contrastText}`,
  },
  compactDocRow: {
    // @ts-ignore
    borderBottom: `1px solid ${theme.palette.background.contrastText}`,
    padding: "14px 5px",
    fontSize: 16,
  },
  compactDocName: {
    fontWeight: 700,
  },
  statusText: {
    fontSize: 16,
    maxWidth: 700,
  },
  statusMailer: {
    fontWeight: "bold",
  },
}));

/**
 * Formats the status of a Github document based on its current state and associated Github repository.
 * If the document is still being processed, it returns a simple "Processing" string.
 * Otherwise, it generates a link to the associated pull request in the Github repository if applicable.
 *
 * @param {Types.GithubDocument} doc - The Github document whose status is to be formatted.
 * @param {{[key: string] : Types.GithubRepo}} repoMap - A map of Github repositories, keyed by their IDs.
 * @returns {JSX.Element} A JSX element containing the formatted status and, if applicable, a link to the associated pull request.
 */
function formatStatus(
  /** @type {Types.GithubDocument} */ doc,
  /** @type {{[key: string] : Types.GithubRepo}} */ repoMap,
) {
  let prStatus;
  switch (doc.status) {
    case "processing":
      return <>Processing</>;
    case "failed":
      return <>Failed</>;
    case "pr_opened":
      prStatus = "PR Created";
      break;
    case "pr_merged":
      prStatus = "PR Merged";
      break;
    case "pr_closed":
      prStatus = "PR Closed without merge";
      break;
    default:
      // programmer error causing unknown status
      return <>Processing</>;
  }

  const repo = repoMap[doc.github_repo_id];
  const repoUrl = repo["external_repo_data"]?.url; // TODO: should separate this from repo response
  const prNumber = doc.pull_request_number;
  const prLink = `${repoUrl}/pull/${prNumber}`;
  const prLinkStyle = { color: "#0092C7", textDecoration: "none" };

  return (
    <>
      {prStatus} (
      <a target="_blank" rel="noreferrer" href={prLink} style={prLinkStyle}>
        #{prNumber}
      </a>
      )
    </>
  );
}

/**
 * Formats the 'status_updated' field of a document into a human-readable date.
 * If the document was updated today or yesterday, it returns "Today" or "Yesterday" respectively.
 * Otherwise, it returns the date in the format "Month Day, Year".
 * If the document has no 'status_updated' field, it returns "-".
 * Assumes that the timestamp from the database server uses UTC time.
 *
 * @param {Object} doc - The document to format.
 * @returns {string} The formatted last updated date.
 */
function formatLastUpdated(doc) {
  if (!doc.status_updated) {
    return "-";
  }
  // assumes that the db server that generates this timestamp uses UTC time.
  // Adding trailing 'Z' signifies UTC timezone
  const updatedDate = new Date(doc.status_updated + "Z");
  const today = new Date();
  if (updatedDate.toDateString() === today.toDateString()) {
    return "Today";
  }
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  if (updatedDate.toDateString() === yesterday.toDateString()) {
    return "Yesterday";
  }
  return updatedDate.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function statusMessage({
  /** @type {string} */ body,
  /** @type {string | undefined} */ mailto,
  classes,
}) {
  return (
    <Typography className={classes.statusText}>
      {body}{" "}
      {mailto !== undefined && (
        <Link className={classes.statusMailer} href="mailto:info@eave.fyi">
          {mailto}
        </Link>
      )}
    </Typography>
  );
}

/**
 * Renders the content of the dashboard based on the state of API documentation fetching. It displays error messages, loading states, and API documentation.
 * It also handles user interactions such as row clicks and mouse overs.
 * Shows a loading spinner while fetching API documentation.
 * If API documentation is empty, informs the user that Eave is searching for Express APIs.
 * If the 'compact' prop is true, renders a compact view of the API documentation.
 * Otherwise, renders a table view of the API documentation.
 *
 * @param {Object} classes - CSS classes for styling the rendered content.
 * @param {Types.DashboardTeam} team - The team object containing API documentation fetching state and repository information.
 * @param {boolean} compact - Determines whether to render a compact view or a table view of the API documentation.
 */
function renderContent(
  classes,
  /** @type {Types.DashboardTeam} */ team,
  compact,
) {
  const {
    apiDocsErroring,
    apiDocsLoading,
    apiDocsFetchCount,
    apiDocs,
    apiDocsJobStatusLoading,
    apiDocsJobs,
    repos,
    apiDocsRequestHasSucceededAtLeastOnce,
  } = team;

  const loadingWheel = (
    <div className={classes.loader}>
      <CircularProgress color="inherit" />
    </div>
  );

  /**
   * This check:
   * a) prevents the table from flashing every time it's loading
   * b) prevents the whole dash from showing an error if the table already loaded but there is an error later.
   */
  if (apiDocsFetchCount === 0) {
    if (apiDocsErroring && !apiDocsRequestHasSucceededAtLeastOnce) {
      return (
        <Typography color="error" className={classes.statusText}>
          ERROR: Unable to fetch API documentation.
        </Typography>
      );
    }
    if (apiDocsLoading) {
      return loadingWheel;
    }
  }

  // no docs created in DB yet; check job status to find why
  if (apiDocs.length === 0) {
    if (apiDocsJobStatusLoading) {
      return loadingWheel;
    }
    const processingMessage = statusMessage({
      body: "Eave is currently searching for Express APIs within your repositories. This may take some time. Please check back for any documentation created.",
      mailto: undefined,
      classes,
    });

    if (!apiDocsJobs || apiDocsJobs.every((job) => job.state === "running")) {
      return processingMessage;
    }
    if (apiDocsJobs.every((job) => job.last_result === "error")) {
      return statusMessage({
        body: "Oops, looks like something went wrong, and we're actively investigating the issue. Please check back again shortly or feel free to",
        mailto: "reach out to us at info@eave.fyi",
        classes,
      });
    }
    if (
      apiDocsJobs.every(
        (job) =>
          job.last_result === "no_api_found" || job.last_result === "error",
      )
    ) {
      return statusMessage({
        body: `We weren’t able to detect any Express APIs to document at this time.
          We're working on expanding support for additional languages and
          frameworks in the near future. Questions, comments, or requests?`,
        mailto: "Send us a message at info@eave.fyi",
        classes,
      });
    }

    // fallback
    return processingMessage;
  }
  const repoMap = mapReposById(repos);
  const handleRowClick = (e, /** @type {Types.GithubDocument} */ doc) => {
    const filePath = doc.file_path;
    const isProcessing = doc.status === "processing";
    const isLink = e.target.tagName === "A";
    if (filePath && !isProcessing && !isLink) {
      const repo = repoMap[doc.github_repo_id];
      const repoUrl = repo["external_repo_data"]?.url;
      if (repoUrl) {
        window.open(`${repoUrl}/blob/main/${filePath}`);
      }
    }
  };
  const handleRowMouseOver = (e, doc) => {
    const filePath = doc.file_path;
    const isProcessing = doc.status === "processing";
    if (filePath && !isProcessing) {
      const tr = e.target.closest("tr");
      tr.style.setProperty("background-color", "#3E3E3E");
    }
  };
  const handleRowMouseOut = (e, _doc) => {
    const tr = e.target.closest("tr");
    tr.style.removeProperty("background-color");
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
            <td className={classes.docTableData}>
              {formatStatus(doc, repoMap)}
            </td>
            <td className={classes.docTableData}>{formatLastUpdated(doc)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

const APIDocumentation = () => {
  const { team, getTeamAPIDocs, getTeamApiDocsJobsStatuses } = useTeam();
  const [compact, setCompact] = useState(window.innerWidth < 900);
  const classes = makeClasses();

  useEffect(() => {
    getTeamAPIDocs();
    getTeamApiDocsJobsStatuses();
    const interval = setInterval(getTeamAPIDocs, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleResize = () => setCompact(window.innerWidth < 900);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
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
