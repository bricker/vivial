import { useContext } from 'react';

import { AppContext } from '../context/Provider.js';
import { AUTH_MODAL_STATE } from '../constants.js';

const useAuthModal = () => {
  const { authModal } = useContext(AppContext);
  const [modalState, setModalState] = authModal;

  return {
    modalState,
    setModalState,
    isOpen: modalState.isOpen,
    openModal: (mode) => {
      setModalState((prevState) => ({
        ...prevState,
        ...(mode && mode !== prevState.mode && { mode }),
        isOpen: true,
      }));
    },
    closeModal: () => setModalState((prevState) => ({ ...prevState, isOpen: false })),
    isLoginMode: modalState.mode === AUTH_MODAL_STATE.LOGIN,
    isSignupMode: modalState.mode === AUTH_MODAL_STATE.SIGNUP,
  };
};

export default useAuthModal;
