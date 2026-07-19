import { type PropsWithChildren } from 'react';

const Page = ({ children }: PropsWithChildren) => (
  <div className="min-h-screen w-full">{children}</div>
);

export default Page;
