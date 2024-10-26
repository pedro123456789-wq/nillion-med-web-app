"use client";

import { useState } from "react";
import Link from "next/link";
import Header from "@/components/ui/Header";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";

interface DiagnosisResult {
  label: string;
  probability: number;
}

export default function Diagnosis() {
  const baseUrl = "http://127.0.0.1:8080/api";

  const [diagnosisMethod, setDiagnosisMethod] = useState<
    "image" | "text" | null
  >(null);
  const [symptoms, setSymptoms] = useState<string>("");
  const [diagnosis, setDiagnosis] = useState<DiagnosisResult[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (symptoms.length === 0){
      toast({
        title: "Invalid input", 
        description: "Fill in the text field", 
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);

    const resp = await fetch(`${baseUrl}/dx/send_text`, {
      method: "POST", 
      body: JSON.stringify({
        symptoms
      }), 
      headers: {
        "Content-Type": "application/json"
      }
    })

    if (!resp.ok){
      setIsLoading(false);
      toast({
        title: "Error", 
        description: "Server error getting diagnosis", 
        variant: "destructive"
      });
      return;
    }

    try {
      const json = await resp.json();
      setDiagnosis(json.predictions);
      console.log(json.predictions);
      setIsLoading(false);
    } catch (error){
      console.error(error);
      toast({
        title: "Error", 
        description: "Error getting diagnosis", 
        variant: "destructive"
      });
    }

    setIsLoading(false);
  };

  if (isLoading){
    return (
      <div className="h-screen flex flex-col items-center justify-center">
        <span className="loading loading-ring loading-lg"></span>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow flex flex-col items-center justify-center p-6 md:p-24">
        <Card className="w-full max-w-md mb-6">
          <CardHeader>
            <CardTitle>Symptom Diagnosis</CardTitle>
            <CardDescription>
              Describe your symptoms for an AI-assisted diagnosis
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent>
              <div className="flex flex-col space-y-4">
                <Textarea
                  placeholder="Describe your symptoms here..."
                  value={symptoms}
                  onChange={(e) => setSymptoms(e.target.value)}
                  rows={6}
                  className="w-full"
                />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col items-center">
              <Button
                type="submit"
                className="w-full mb-4"
                disabled={!symptoms.trim()}
              >
                Submit for Diagnosis
              </Button>
            </CardFooter>
          </form>
        </Card>

        {diagnosis.length > 0 && (
          <Card className="w-full max-w-md mb-6">
            <CardHeader>
              <CardTitle>Diagnosis Results</CardTitle>
              <CardDescription>
              Likelihood of diagnosis based on symptoms. 
              {/* This is not a definitive diagnosis and should be discussed with a healthcare professional. */}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {diagnosis.map((result, index) => (
                  <li key={index} className="flex justify-between items-center">
                    <span>{result.label}</span>
                    <span className="font-semibold">
                      {(result.probability * 100).toFixed(2)}%
                    </span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        <Link href="/" className="mt-8">
          <Button variant="outline">Back to Home</Button>
        </Link>
        <div className="mt-8 text-center text-sm text-gray-500 max-w-md">
          <p className="mb-2">
            <strong>Disclaimer:</strong> This AI-assisted diagnosis tool is for informational purposes only and does not substitute professional medical advice, diagnosis, or treatment.
          </p>
        </div>
      </main>
    </div>
  );
}
