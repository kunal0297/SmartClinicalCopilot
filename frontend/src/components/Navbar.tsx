import type { FC } from 'react';

interface NavbarProps {
  mode: 'light' | 'dark';
  toggleMode: () => void;
}

const Navbar: FC<NavbarProps> = ({ mode, toggleMode }) => {
  return (
    <div>
      {/* Your navbar implementation */}
      <button onClick={toggleMode}>{mode === 'light' ? 'Dark' : 'Light'} Mode</button>
    </div>
  );
};

export default Navbar;