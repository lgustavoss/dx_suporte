import React from "react";
import PageContainer from "../../components/ui/PageContainer";

export default function Dashboard() {
  return (
    <PageContainer>
      <h1 className="text-3xl font-heading font-bold text-primary mb-4">
        Dashboard
      </h1>
      <p className="text-lg text-gray-700 mb-8">
        Bem-vindo ao painel principal!
      </p>
    </PageContainer>
  );
}