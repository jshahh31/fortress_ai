export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="h-full min-h-screen overflow-hidden">
      {children}
    </div>
  );
}
