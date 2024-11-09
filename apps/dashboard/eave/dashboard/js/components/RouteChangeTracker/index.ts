import { useEffect } from "react";
import { useLocation } from "react-router-dom";

const RouteChangeTracker = ({ onRouteChange }: { onRouteChange: (newLocation: string) => void }) => {
  const location = useLocation();

  useEffect(() => {
    onRouteChange(location.pathname);
  }, [location, onRouteChange]);

  return null;
};

export default RouteChangeTracker;
