import { Outlet } from 'react-router-dom';

const DashboardLayout = () => (
  <div>
    <header>Dashboard Header</header>
    <main>
      <Outlet />
    </main>
  </div>
);

export default DashboardLayout;
