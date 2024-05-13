import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import Subpage from './Subpage';
import {
  createBrowserRouter,
  RouterProvider,
} from 'react-router-dom';
import FormPage from './FormPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />
  },
  {
    path: '/page',
    element: <Subpage />
  },
  {
    path: '/form',
    element: <FormPage />
  },
]);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
