import { useContext } from "react";

import { AUTH_MODAL_STATE } from "../constants.js";
import { AppContext } from "../context/Provider.js";

const useAuthModal = () => {
  const { authModalCtx } = useContext(AppContext);
  const [authModal, setAuthModal] = authModalCtx;

  return {
    authModal,
    setAuthModal,
    isOpen: authModal.isOpen,
    openModal: (mode) => {
      setAuthModal((prevState) => ({
        ...prevState,
        ...(mode && mode !== prevState.mode && { mode }),
        isOpen: true,
      }));
    },
    closeModal: () => setAuthModal((prevState) => ({ ...prevState, isOpen: false })),
    isLoginMode: authModal.mode === AUTH_MODAL_STATE.LOGIN,
    isSignupMode: authModal.mode === AUTH_MODAL_STATE.SIGNUP,
  };
};

export default useAuthModal;
