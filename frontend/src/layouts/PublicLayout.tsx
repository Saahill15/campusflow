import { Outlet } from 'react-router-dom';

const PublicLayout = () => (
  <div>
    <header>Public Header</header>
    <main>
      <Outlet />
    </main>
    <footer>Public Footer</footer>
  </div>
);

export default PublicLayout;
