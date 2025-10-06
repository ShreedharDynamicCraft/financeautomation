/// <reference types="react-scripts" />

// CSS Modules
declare module '*.css' {
  const content: { [className: string]: string };
  export default content;
}

declare module '*.scss' {
  const content: { [className: string]: string };
  export default content;
}

// Side-effect imports for CSS files
declare module 'react-toastify/dist/ReactToastify.css';

declare module 'framer-motion' {
  import * as React from 'react';
  
  export interface MotionProps extends React.HTMLAttributes<HTMLElement> {
    initial?: any;
    animate?: any;
    exit?: any;
    transition?: any;
    whileHover?: any;
    whileTap?: any;
    variants?: any;
  }

  export const motion: {
    div: React.ForwardRefExoticComponent<MotionProps & React.RefAttributes<HTMLDivElement>>;
    button: React.ForwardRefExoticComponent<MotionProps & React.RefAttributes<HTMLButtonElement>>;
    section: React.ForwardRefExoticComponent<MotionProps & React.RefAttributes<HTMLElement>>;
    [key: string]: React.ForwardRefExoticComponent<MotionProps & React.RefAttributes<any>>;
  };

  export const AnimatePresence: React.FC<{
    children: React.ReactNode;
    mode?: 'wait' | 'sync' | 'popLayout';
    initial?: boolean;
  }>;
}

declare namespace JSX {
  interface IntrinsicElements {
    input: React.DetailedHTMLProps<React.InputHTMLAttributes<HTMLInputElement>, HTMLInputElement>;
  }
}
