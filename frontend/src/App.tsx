import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import { PlantDetailPage } from "./pages/PlantDetailPage";
import { PlantNewPage } from "./pages/PlantNewPage";
import { PlantsPage } from "./pages/PlantsPage";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<DashboardPage />} />
            <Route path="plants" element={<PlantsPage />} />
            <Route path="plants/new" element={<PlantNewPage />} />
            <Route path="plants/:id" element={<PlantDetailPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
