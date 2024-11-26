import React from 'react';

export const Heading = ({ children, size = 'md', className = '' }) => {
  const sizeStyles = {
    sm: 'text-lg font-semibold',
    md: 'text-xl font-semibold',
    lg: 'text-2xl font-bold',
    xl: 'text-3xl font-bold',
  };

  return (
    <h2 className={`${sizeStyles[size]} ${className}`}>
      {children}
    </h2>
  );
};

export const Paragraph = ({ children, className = '' }) => {
  return (
    <p className={`text-gray-700 ${className}`}>
      {children}
    </p>
  );
};

export const Link = ({ children, href, className = '' }) => {
  return (
    <a
      href={href}
      className={`text-blue-500 hover:text-blue-600 ${className}`}
    >
      {children}
    </a>
  );
};