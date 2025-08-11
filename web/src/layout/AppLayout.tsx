import { SidebarProvider} from "../context/SidebarContext";
import { Outlet } from "react-router";
import AppHeader from "./AppHeader";


const AppLayout: React.FC = () => {
  return (
    <SidebarProvider>
      <div className="min-h-screen flex flex-col">
        <AppHeader />
        <div className="p-4 w-full flex-1 flex flex-col">
          <Outlet />
        </div>
      </div>
    </SidebarProvider>
  );
};

export default AppLayout;
