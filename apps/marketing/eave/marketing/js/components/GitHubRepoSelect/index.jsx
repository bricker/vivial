import React from "react";
import { makeStyles } from "@material-ui/styles";
import { FormGroup, FormControlLabel, Checkbox } from "@material-ui/core";


const makeClasses = makeStyles(() => ({

}));

const GitHubRepoSelect = ({ repos, selectedRepoIds, onSelect }) => {
  const classes = makeClasses();
  const handleSelect = (event) => {
    onSelect(event.target.value);
  };

  return (
    <FormGroup>
      <FormControlLabel
        value="default"
        label="Default (All)"
        onChange={handleSelect}
        control={<Checkbox checked={repos.length === selectedRepoIds.length} />}
      />
      {repos.map((repo) => (
        <FormControlLabel
          key={repo.id}
          value={repo.id}
          label={repo.name}
          onChange={handleSelect}
          control={<Checkbox checked={selectedRepoIds.includes(repo.id)} />}
        />
      ))}
    </FormGroup>
  );
}

export default GitHubRepoSelect;
