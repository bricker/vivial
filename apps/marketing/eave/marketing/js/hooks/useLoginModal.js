import { useState } from 'react';

import { AUTH_MODAL_STATE } from '../constants.js';

const useLoginModal = () => {
  const [modalState, setModalState] = useState({
    isOpen: true,
    mode: AUTH_MODAL_STATE.LOGIN,
  });

  return {
    modalState,
    setModalState,
    isOpen: modalState.isOpen,
    isLoginMode: modalState.mode === AUTH_MODAL_STATE.LOGIN,
    isSignupMode: modalState.mode === AUTH_MODAL_STATE.SIGNUP,
  };
};

export default useLoginModal;
