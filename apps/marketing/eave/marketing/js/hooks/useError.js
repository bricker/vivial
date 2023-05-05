import { useContext } from 'react';

import { AppContext } from '../context/Provider.js';

const useError = () => {
  const { error } = useContext(AppContext);
  const [errorState, setErrorState] = error;

  return {
    errorState,
    setErrorState,
  };
};

export default useError;
