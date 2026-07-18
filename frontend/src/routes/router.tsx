import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { AppRoutes } from './routes';
import HomePage from '../pages/HomePage';
import LoginPage from '../pages/LoginPage';
import EventsPage from '../pages/EventsPage';
import ProfilePage from '../pages/ProfilePage';
import DashboardPage from '../pages/DashboardPage';
import AdminPage from '../pages/AdminPage';
import NotFoundPage from '../pages/NotFoundPage';
import PublicLayout from '../layouts/PublicLayout';
import AuthLayout from '../layouts/AuthLayout';
import DashboardLayout from '../layouts/DashboardLayout';

const Router = () => (
  <BrowserRouter>
    <Routes>
      <Route element={<PublicLayout />}>
        <Route path={AppRoutes.HOME} element={<HomePage />} />
        <Route path={AppRoutes.EVENTS} element={<EventsPage />} />
        <Route path={AppRoutes.LOGIN} element={<LoginPage />} />
      </Route>

      <Route element={<AuthLayout />}>
        <Route path={AppRoutes.PROFILE} element={<ProfilePage />} />
      </Route>

      <Route element={<DashboardLayout />}>
        <Route path={AppRoutes.DASHBOARD} element={<DashboardPage />} />
        <Route path={AppRoutes.ADMIN} element={<AdminPage />} />
      </Route>

      <Route path={AppRoutes.NOT_FOUND} element={<NotFoundPage />} />
    </Routes>
  </BrowserRouter>
);

export default Router;
