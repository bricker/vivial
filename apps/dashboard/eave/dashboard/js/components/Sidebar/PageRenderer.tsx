import React from "react";
import { Route, Routes } from "react-router-dom";
import Glossary from "../Pages/Dashboard/Glossary/index";
import Insights from "../Pages/Dashboard/Insights/index";
import Settings from "../Pages/Dashboard/Settings/index";
import Setup from "../Pages/Dashboard/Setup/index";
import TeamManagement from "../Pages/Dashboard/TeamManagement/index";

const PageRenderer = () => {
  return (
    <>
      <Routes>
        <Route path="/setup" element={<Setup />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/glossary" element={<Glossary />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="/team" element={<TeamManagement />} />
      </Routes>
    </>
  );
};

export default PageRenderer;
