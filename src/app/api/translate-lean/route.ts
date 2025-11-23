import { NextRequest, NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";

export async function POST(req: NextRequest) {
    try {
        const { theoremMarkdown } = await req.json();

        if (!theoremMarkdown) {
            return NextResponse.json({ error: "Missing theoremMarkdown" }, { status: 400 });
        }

        const apiKey = process.env.ANTHROPIC_API_KEY;
        if (!apiKey) {
            console.error("ANTHROPIC_API_KEY is not set");
            return NextResponse.json({ error: "Server configuration error" }, { status: 500 });
        }

        const anthropic = new Anthropic({ apiKey });

        const msg = await anthropic.messages.create({
            model: "claude-3-opus-20240229",
            max_tokens: 4000,
            system: "Translate the extracted theorem+proof into Lean 4 using mathlib. Return ONLY valid Lean code. No commentary.",
            messages: [{ role: "user", content: theoremMarkdown }],
        });

        const content = msg.content[0];
        if (content.type !== 'text') {
            throw new Error("Unexpected response type from Claude");
        }
        const text = content.text;

        // Extract code block if present, otherwise assume full text is code
        const codeMatch = text.match(/```lean([\s\S]*?)```/) || text.match(/```([\s\S]*?)```/);
        const leanCode = codeMatch ? codeMatch[1].trim() : text.trim();

        return NextResponse.json({ leanCode });
    } catch (error) {
        console.error("Error in translate-lean route:", error);
        return NextResponse.json({ error: "Lean translation failed" }, { status: 500 });
    }
}
