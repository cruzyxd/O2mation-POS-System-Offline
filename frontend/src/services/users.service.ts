import { authedFetch, readJson } from "../lib/api";
import type {
  CreateUserRequest,
  DeleteUserRequest,
  ListUsersResponse,
  ToggleUserActiveRequest,
  UpdateUserRequest,
  UserWithPassword,
} from "../types/users.types";

export async function listUsers(accessToken: string): Promise<UserWithPassword[]> {
  const response = await authedFetch("/users");
  const data = await readJson<ListUsersResponse>(response);
  return data.users;
}

export async function createUser(
  accessToken: string,
  request: CreateUserRequest
): Promise<UserWithPassword> {
  const response = await authedFetch("/users", {
    method: "POST",
    body: JSON.stringify(request),
  });
  return readJson<UserWithPassword>(response);
}

export async function updateUser(
  accessToken: string,
  userId: number,
  request: UpdateUserRequest
): Promise<UserWithPassword> {
  const response = await authedFetch(`/users/${userId}`, {
    method: "PATCH",
    body: JSON.stringify(request),
  });
  return readJson<UserWithPassword>(response);
}

export async function toggleUserActive(
  accessToken: string,
  userId: number,
  request: ToggleUserActiveRequest
): Promise<{ id: number; is_active: boolean }> {
  const response = await authedFetch(`/users/${userId}/activate`, {
    method: "PATCH",
    body: JSON.stringify(request),
  });
  return readJson<{ id: number; is_active: boolean }>(response);
}

export async function deleteUser(
  accessToken: string,
  userId: number,
  request: DeleteUserRequest
): Promise<{ success: boolean; id: number }> {
  const response = await authedFetch(`/users/${userId}`, {
    method: "DELETE",
    body: JSON.stringify(request),
  });
  return readJson<{ success: boolean; id: number }>(response);
}
