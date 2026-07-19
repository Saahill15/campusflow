import React from 'react';
import { cn } from './cn';

export interface AvatarProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  initials?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const Avatar: React.FC<AvatarProps> = ({ initials, src, size = 'md', className, alt = 'avatar', ...props }) => {
  const sizes: Record<string, string> = { sm: 'h-8 w-8 text-sm', md: 'h-10 w-10 text-base', lg: 'h-14 w-14 text-xl' };
  return (
    <div className={cn('inline-flex items-center justify-center rounded-full overflow-hidden bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-200', sizes[size], className)}>
      {src ? <img src={src} alt={alt} {...props} /> : <span className="font-medium">{initials ?? alt.charAt(0).toUpperCase()}</span>}
    </div>
  );
};

Avatar.displayName = 'Avatar';
