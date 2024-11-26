export const Button = ({
  children,
  onClick,
  className = '',
  disabled = false,
  variant = 'primary',
}) => {
  const variantStyles = {
    primary:
      'bg-blue-500 hover:bg-blue-600 text-white focus:ring-blue-500 focus:border-blue-500',
    secondary:
      'bg-white border border-gray-300 text-gray-700 hover:bg-gray-100 focus:ring-gray-300 focus:border-gray-300',
    danger:
      'bg-red-500 hover:bg-red-600 text-white focus:ring-red-500 focus:border-red-500',
  };

  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-md text-sm font-medium transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 ${variantStyles[variant]} ${className}`}
      disabled={disabled}
    >
      {children}
    </button>
  );
};