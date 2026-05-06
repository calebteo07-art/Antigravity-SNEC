import { createBrowserRouter } from "react-router";
import { OnboardingScreen } from "./components/OnboardingScreen";
import { DashboardScreen } from "./components/DashboardScreen";
import { ChatScreen } from "./components/ChatScreen";
import { CaseListScreen } from "./components/CaseListScreen";
import { CaseSessionScreen } from "./components/CaseSessionScreen";
import { FlashcardScreen } from "./components/FlashcardScreen";
import { SummaryScreen } from "./components/SummaryScreen";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: OnboardingScreen,
  },
  {
    path: "/dashboard",
    Component: DashboardScreen,
  },
  {
    path: "/chat",
    Component: ChatScreen,
  },
  {
    path: "/cases",
    Component: CaseListScreen,
  },
  {
    path: "/cases/:caseId",
    Component: CaseSessionScreen,
  },
  {
    path: "/flashcards",
    Component: FlashcardScreen,
  },
  {
    path: "/summary",
    Component: SummaryScreen,
  },
]);
