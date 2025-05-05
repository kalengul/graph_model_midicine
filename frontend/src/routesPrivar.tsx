import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAppSelector } from './redux/hooks';
import { RootState } from './redux/store';

interface PrivateRouteProps {
  children: React.ReactNode;
}

export const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const { isAuthenticated } = useAppSelector((state: RootState) => state.auth);

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};