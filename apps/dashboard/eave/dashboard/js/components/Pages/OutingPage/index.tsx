import React from "react";
import { useParams } from "react-router-dom";

const OutingPage = () => {
  const params = useParams();
  console.log(params["outingId"]);
  return <div>Your date is at mcdonglsds. proceed directly to mcdonagle dont pass go dont collect $200</div>;
};

export default OutingPage;
