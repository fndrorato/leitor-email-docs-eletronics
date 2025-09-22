import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import SignIn from "./pages/AuthPages/SignIn";
import SignUp from "./pages/AuthPages/SignUp";
// import NotFound from "./pages/OtherPage/NotFound";
import UserProfiles from "./pages/UserProfiles";
import UsersList from "./pages/Users/UsersList";
import ChannelsList from "./pages/Channels/ChannelsList";
import Videos from "./pages/UiElements/Videos";
import Images from "./pages/UiElements/Images";
import Alerts from "./pages/UiElements/Alerts";
import Badges from "./pages/UiElements/Badges";
import Avatars from "./pages/UiElements/Avatars";
import Buttons from "./pages/UiElements/Buttons";
import LineChart from "./pages/Charts/LineChart";
import BarChart from "./pages/Charts/BarChart";
import Calendar from "./pages/Calendar";
import BasicTables from "./pages/Tables/BasicTables";
import FormElements from "./pages/Forms/FormElements";
import Blank from "./pages/Blank";
import AppLayout from "./layout/AppLayout";
import { ScrollToTop } from "./components/common/ScrollToTop";
import Home from "./pages/Dashboard/Home";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import ConfigPage from "./pages/Config/ConfigPage";
import SendMessagePage from "./pages/Channels/SendMessagePage";
import { AuthProvider } from "./context/AuthContext";
import Posts from "./pages/Reports/Posts";
import FilterEletronicDocs from "./pages/FilterEletronicDocs";
import { FilterProvider } from "./context/FilterContext";

export default function App() {
  console.log("API base URL:", import.meta.env.VITE_API_BASE_URL);
  return (
    <AuthProvider>
      <Router>
        <ScrollToTop />
        <Routes>
          <Route element={<ProtectedRoute redirectPath="/signin" />}>
            <Route element={<FilterProvider><AppLayout /></FilterProvider>}>
              <Route path="/" element={<Navigate to="/filter" replace />} />
              <Route path="/filter" element={<FilterEletronicDocs />} />
              <Route path="/home" element={<Home />} />
              {/* Others Page */}
              <Route path="/profile" element={<UserProfiles />} />
              <Route path="/users" element={<UsersList />} />
              <Route path="/channels" element={<ChannelsList />} />
              <Route path="/channels/default/:channelId" element={<SendMessagePage />} />
              <Route path="/calendar" element={<Calendar />} />
              <Route path="/blank" element={<Blank />} />
              <Route path="/config" element={<ConfigPage />} />

              {/* Reports */}
              <Route path="/reports/posts" element={<Posts />} />

              {/* Forms */}
              <Route path="/form-elements" element={<FormElements />} />

              {/* Tables */}
              <Route path="/basic-tables" element={<BasicTables />} />

              {/* Ui Elements */}
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/avatars" element={<Avatars />} />
              <Route path="/badge" element={<Badges />} />
              <Route path="/buttons" element={<Buttons />} />
              <Route path="/images" element={<Images />} />
              <Route path="/videos" element={<Videos />} />

              {/* Charts */}
              <Route path="/line-chart" element={<LineChart />} />
              <Route path="/bar-chart" element={<BarChart />} />
            </Route>
          </Route>

          {/* Rotas de autenticação e fallback, fora do AppLayout */}
          <Route path="/signin" element={<SignIn onLoginSuccess={() => {}} />} />
          <Route path="/signup" element={<SignUp />} />

          {/* Fallback Route */}
          <Route path="*" element={<Navigate to="/filter" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
