import { Outfit } from "next/font/google";
import "./globals.css";

const outfit = Outfit({ 
  subsets: ["latin"], 
  weight: ["300", "400", "500", "600", "700"] 
});

export const metadata = {
  title: "RetinAI - Dépistage Intelligent de la Rétinopathie Diabétique",
  description: "Système d'assistance clinique par intelligence artificielle (ONNX) et orchestration d'agents LangGraph.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
      </head>
      <body className={outfit.className}>{children}</body>
    </html>
  );
}
