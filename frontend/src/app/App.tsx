import { Route, Routes } from "react-router-dom";

import { Layout } from "./Layout";
import { ProtectedRoute } from "./ProtectedRoute";
import { AdminUsersPage } from "../pages/AdminUsersPage";
import { ArticleDetailPage } from "../pages/ArticleDetailPage";
import { ArticleFormPage } from "../pages/ArticleFormPage";
import { ArticlesPage } from "../pages/ArticlesPage";
import { DashboardPage } from "../pages/DashboardPage";
import { LoginPage } from "../pages/LoginPage";
import { NewsDetailPage } from "../pages/NewsDetailPage";
import { NewsFormPage } from "../pages/NewsFormPage";
import { NewsPage } from "../pages/NewsPage";
import { ProfilePage } from "../pages/ProfilePage";
import { SearchPage } from "../pages/SearchPage";
import { TaskDetailPage } from "../pages/TaskDetailPage";
import { TaskFormPage } from "../pages/TaskFormPage";
import { TasksPage } from "../pages/TasksPage";
import { TaxonomyPage } from "../pages/TaxonomyPage";

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="articles" element={<ArticlesPage />} />
          <Route path="articles/new" element={<ProtectedRoute roles={["admin", "editor"]} />}>
            <Route index element={<ArticleFormPage />} />
          </Route>
          <Route path="articles/:id" element={<ArticleDetailPage />} />
          <Route path="articles/:id/edit" element={<ProtectedRoute roles={["admin", "editor"]} />}>
            <Route index element={<ArticleFormPage />} />
          </Route>
          <Route path="news" element={<NewsPage />} />
          <Route path="news/new" element={<ProtectedRoute roles={["admin", "editor"]} />}>
            <Route index element={<NewsFormPage />} />
          </Route>
          <Route path="news/:id" element={<NewsDetailPage />} />
          <Route path="news/:id/edit" element={<ProtectedRoute roles={["admin", "editor"]} />}>
            <Route index element={<NewsFormPage />} />
          </Route>
          <Route path="tasks" element={<TasksPage />} />
          <Route path="tasks/new" element={<ProtectedRoute roles={["admin", "editor"]} />}>
            <Route index element={<TaskFormPage />} />
          </Route>
          <Route path="tasks/:id" element={<TaskDetailPage />} />
          <Route path="tasks/:id/edit" element={<ProtectedRoute roles={["admin", "editor"]} />}>
            <Route index element={<TaskFormPage />} />
          </Route>
          <Route path="taxonomy" element={<TaxonomyPage />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="admin/users" element={<ProtectedRoute roles={["admin"]} />}>
            <Route index element={<AdminUsersPage />} />
          </Route>
        </Route>
      </Route>
    </Routes>
  );
}
