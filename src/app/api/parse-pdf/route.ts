import { NextRequest, NextResponse } from "next/server";
import Groq from "groq-sdk";
import * as pdfjsLib from "pdfjs-dist/legacy/build/pdf.mjs";

// Force Node.js runtime to ensure compatibility with file system and buffer operations
export const runtime = "nodejs";

export async function POST(req: NextRequest) {
    console.log("--- [API] Starting PDF Parse Request (Model: llama-3.1-70b-versatile via Groq) ---");

    try {
        // 1. Check Environment
        const apiKey = process.env.GROQ_API_KEY;
        if (!apiKey) {
            console.error("[API] ❌ GROQ_API_KEY is missing");
            return NextResponse.json({ error: "Server configuration error" }, { status: 500 });
        }

        // 2. Parse Form Data
        const formData = await req.formData();
        const file = formData.get("file") as File;
        if (!file) {
            return NextResponse.json({ error: "No file uploaded" }, { status: 400 });
        }

        // 3. Buffer Conversion
        const arrayBuffer = await file.arrayBuffer();

        // 4. PDF Text Extraction using pdfjs-dist legacy build
        // This is the most reliable way to extract text in a Node environment without canvas dependencies
        let rawPdfText = "";

        try {
            // Configure standard font data to avoid needing canvas
            const loadingTask = pdfjsLib.getDocument({
                data: new Uint8Array(arrayBuffer),
                useSystemFonts: true,
                disableFontFace: true, // Critical for Node.js environment
            });

            const doc = await loadingTask.promise;
            console.log(`[API] ✅ PDF Loaded. Pages: ${doc.numPages}`);

            // Extract text from all pages
            for (let i = 1; i <= doc.numPages; i++) {
                const page = await doc.getPage(i);
                const content = await page.getTextContent();
                // Join items with a space to preserve word separation
                const pageText = content.items
                    .map((item: any) => item.str)
                    .join(" ");
                rawPdfText += pageText + "\n\n";
            }

            if (!rawPdfText || rawPdfText.length < 10) {
                console.warn("[API] ⚠️ PDF text extraction yielded little/no text.");
            } else {
                console.log(`[API] ✅ Extracted ${rawPdfText.length} characters.`);
            }

        } catch (err) {
            console.error("[API] ❌ PDF extraction failed:", err);
            return NextResponse.json(
                { error: "Could not extract text from PDF. The file might be corrupted." },
                { status: 500 }
            );
        }

        // 5. Groq API Call
        const groq = new Groq({ apiKey });

        console.log(`[API] 🚀 Calling Groq...`);

        const completion = await groq.chat.completions.create({
            messages: [
                {
                    role: "system",
                    content: "Extract ONLY the first theorem and its proof from the provided text. Return Markdown with sections: # Theorem, ## Statement, ## Proof. If no theorem is found, state that clearly.",
                },
                {
                    role: "user",
                    content: rawPdfText.substring(0, 32000), // Safety cap for context window
                },
            ],
            model: "llama-3.1-70b-versatile",
            temperature: 0.1,
        });

        const text = completion.choices[0]?.message?.content;

        if (!text) {
            return NextResponse.json({ error: "LLM returned no text" }, { status: 500 });
        }

        return NextResponse.json({ theoremMarkdown: text, text: text });

    } catch (error) {
        console.error("[API] 💥 Unhandled Exception:", error);
        return NextResponse.json({ error: "Internal server error" }, { status: 500 });
    }
}
