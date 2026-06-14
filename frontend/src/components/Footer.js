export default function Footer() {
  return (
    <footer className="border-t border-border bg-card text-card-foreground py-8 w-full mt-auto">
      <div className="container mx-auto max-w-7xl px-4 flex flex-col md:flex-row justify-between items-center opacity-80 text-sm">
        <p>&copy; {new Date().getFullYear()} AI Career Coach. All rights reserved.</p>
        <div className="flex space-x-4 mt-4 md:mt-0">
          <span className="hover:text-primary cursor-pointer transition-colors">Privacy Policy</span>
          <span className="hover:text-primary cursor-pointer transition-colors">Terms of Service</span>
          <span className="hover:text-primary cursor-pointer transition-colors">Contact Support</span>
        </div>
      </div>
    </footer>
  );
}
