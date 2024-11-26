export const Input = ({
    type = 'text',
    id,
    value,
    onChange,
    placeholder,
    className = '',
    error,
  }) => {
    const inputClasses = `
      block
      w-full
      px-4
      py-2
      text-gray-900
      bg-white
      border
      rounded-md
      focus:outline-none
      focus:ring-2
      focus:ring-blue-500
      focus:border-blue-500
      ${error ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'}
      ${className}
    `;
  
    return (
      <div>
        <input
          type={type}
          id={id}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className={inputClasses}
        />
        {error && <div className="text-red-500 mt-1">{error}</div>}
      </div>
    );
  };