import type { Article, RoleName, User } from "../types/api";

export function hasAnyRole(user: User | null, roles: RoleName[]): boolean {
  return Boolean(user && roles.includes(user.role.name));
}

export function canManageContent(user: User | null, item?: Pick<Article, "author_id">): boolean {
  if (!user) {
    return false;
  }
  if (user.role.name === "admin") {
    return true;
  }
  return user.role.name === "editor" && item?.author_id === user.id;
}
