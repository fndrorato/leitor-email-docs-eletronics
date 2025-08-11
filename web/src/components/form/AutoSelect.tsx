import React from 'react';
import AsyncSelect from 'react-select/async';
import type { StylesConfig } from 'react-select';
import Label from './Label';


type Option = {
  value: string;
  label: string;
};

interface AutoSelectProps {
  id?: string;
  label?: string;
  value: string;
  placeholder?: string;
  onChange: (value: string) => void;
  loadOptions: (inputValue: string) => Promise<Option[]>;
}

const customStyles: StylesConfig<Option, false> = {
  control: (base, state) => ({
    ...base,
    minHeight: '2.75rem',
    borderRadius: '0.5rem',
    paddingLeft: '0.75rem',
    paddingRight: '0.25rem',
    fontSize: '0.875rem',
    boxShadow: state.isFocused ? '0 0 0 3px rgba(59, 130, 246, 0.1)' : 'none',
    borderColor: state.isFocused ? '#60A5FA' : '#D1D5DB',
    backgroundColor: 'var(--tw-bg)', // dinâmico com Tailwind
    color: 'var(--tw-text)',         // dinâmico com Tailwind
  }),

  placeholder: (base) => ({
    ...base,
    color: 'var(--tw-placeholder)',
  }),

  singleValue: (base) => ({
    ...base,
    color: 'var(--tw-text)',
  }),

  menu: (base) => ({
    ...base,
    zIndex: 9999,
    backgroundColor: 'var(--tw-bg)',
    borderRadius: '0.5rem',
  }),

  option: (base, state) => ({
    ...base,
    backgroundColor: state.isFocused ? 'var(--tw-bg-hover)' : 'transparent',
    color: 'var(--tw-text)',
    cursor: 'pointer',
  }),

  menuPortal: (base) => ({
    ...base,
    zIndex: 9999,
  }),

  dropdownIndicator: (base) => ({
    ...base,
    paddingRight: '0.5rem',
    color: 'var(--tw-text)',
  }),

  clearIndicator: (base) => ({
    ...base,
    paddingRight: '0.5rem',
    color: 'var(--tw-text)',
  }),
};


const AutoSelect: React.FC<AutoSelectProps> = ({
  id,
  label,
  value,
  placeholder = 'Digite...',
  onChange,
  loadOptions,
}) => {
  const [selectedOption, setSelectedOption] = React.useState<Option | null>(null);

  React.useEffect(() => {
    if (value && (!selectedOption || selectedOption.value !== value)) {
      // Opcional: você pode carregar o label real se quiser
      setSelectedOption({ value, label: value });
    }
  }, [value]);

  return (
    <div className="flex flex-col gap-1 w-[180px]">
      {label && <Label htmlFor={id}>{label}</Label>}
      <AsyncSelect
        instanceId={id}
        cacheOptions
        defaultOptions
        menuPortalTarget={document.body}
        styles={customStyles}
        value={selectedOption}
        loadOptions={loadOptions}
        onChange={(selected) => {
          const selectedValue = selected ? selected.value : '';
          onChange(selectedValue);
          setSelectedOption(selected || null);
        }}
        placeholder={placeholder}
        isClearable
      />
    </div>
  );
};

export default AutoSelect;
