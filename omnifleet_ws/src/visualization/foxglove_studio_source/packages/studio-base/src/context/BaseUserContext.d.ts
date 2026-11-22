/// <reference types="react" />
export type UserType = "unauthenticated" | "authenticated-free" | "authenticated-team" | "authenticated-enterprise";
export interface CurrentUser {
    currentUserType: UserType;
    signIn?: () => void;
    signOut?: () => Promise<void>;
}
declare const BaseUserContext: import("react").Context<CurrentUser>;
export declare function useCurrentUser(): CurrentUser;
export default BaseUserContext;
