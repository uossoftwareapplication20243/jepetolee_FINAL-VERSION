import React from 'react';

export const Grid = ({ children, className = '' }) => {
  return (
    <div className={`grid grid-cols-12 gap-4 ${className}`}>
      {children}
    </div>
  );
};

export const GridItem = ({ children, className = '', colSpan = 1 }) => {
  const colClasses = `col-span-${colSpan}`;

  return (
    <div className={`${colClasses} ${className}`}>
      {children}
    </div>
  );
};