import { type PropsWithChildren } from 'react';

const Container = ({ children }: PropsWithChildren) => (
  <div className="mx-auto max-w-[1280px] px-4">{children}</div>
);

export default Container;
