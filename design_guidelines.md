{
  "meta": {
    "product_name": "GR8 AI Automation",
    "tagline": "Scan any website. Get AI-built automations in minutes.",
    "audience": ["Small business owners", "Marketers", "Entrepreneurs"],
    "brand_attributes": ["trustworthy", "efficient", "modern", "approachable", "automation-first"],
    "visual_personality": "Modern SaaS with Swiss-grid clarity, light warmth, and subtle motion. No gimmicks. Hands-on hero with URL analysis, clear recommendations, and a focused dashboard."
  },

  "typography": {
    "font_pairs": {
      "heading": "Space Grotesk",
      "body": "Figtree",
      "mono": "Source Code Pro"
    },
    "import_examples": [
      "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">",
      "<link href=\"https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=Source+Code+Pro:wght@400;600&display=swap\" rel=\"stylesheet\">"
    ],
    "tailwind_usage": {
      "heading_classes": "font-[\'Space_Grotesk\'] tracking-tight",
      "body_classes": "font-[\'Figtree\']",
      "scales": {
        "h1": "text-4xl sm:text-5xl lg:text-6xl leading-[1.05]",
        "h2": "text-base md:text-lg leading-snug",
        "body": "text-sm md:text-base leading-7",
        "small": "text-xs leading-5"
      }
    }
  },

  "color_system": {
    "note": "Set brand tokens first — do not rely on defaults. Maintain WCAG AA contrast.",
    "palette": {
      "primary_teal": "190 72% 35%",      
      "primary_teal_600": "190 70% 28%",
      "mint": "169 53% 82%",
      "peach": "22 92% 86%",
      "sand": "40 42% 88%",
      "slate_900": "220 15% 12%",
      "slate_700": "220 10% 28%",
      "slate_500": "220 9% 46%",
      "slate_200": "220 16% 90%",
      "white": "0 0% 100%",
      "success": "164 85% 34%",
      "warning": "35 90% 56%",
      "error": "0 72% 54%"
    },
    "css_tokens_override_for_index_css": {
      "paste_under": "@layer base :root",
      "vars": "--background: 0 0% 100%;\n--foreground: 220 15% 12%;\n--card: 0 0% 100%;\n--card-foreground: 220 15% 12%;\n--popover: 0 0% 100%;\n--popover-foreground: 220 15% 12%;\n--primary: 190 72% 35%;\n--primary-foreground: 0 0% 98%;\n--secondary: 40 42% 88%;\n--secondary-foreground: 220 15% 12%;\n--muted: 220 16% 94%;\n--muted-foreground: 220 9% 46%;\n--accent: 22 92% 86%;\n--accent-foreground: 220 15% 12%;\n--destructive: 0 72% 54%;\n--destructive-foreground: 0 0% 98%;\n--border: 220 16% 90%;\n--input: 220 16% 90%;\n--ring: 190 72% 35%;\n--radius: 0.75rem;\n--success: 164 85% 34%;\n--warning: 35 90% 56%;\n--error: 0 72% 54%;"
    },
    "dark_mode_tokens": {
      "paste_under": "@layer base .dark",
      "vars": "--background: 220 15% 10%;\n--foreground: 0 0% 98%;\n--card: 220 15% 12%;\n--card-foreground: 0 0% 98%;\n--primary: 190 72% 40%;\n--primary-foreground: 0 0% 100%;\n--secondary: 220 12% 18%;\n--secondary-foreground: 0 0% 98%;\n--muted: 220 12% 18%;\n--muted-foreground: 220 9% 70%;\n--accent: 22 92% 22%; /* peach becomes subtle tint */\n--accent-foreground: 0 0% 98%;\n--destructive: 0 62% 40%;\n--destructive-foreground: 0 0% 98%;\n--border: 220 12% 22%;\n--input: 220 12% 22%;\n--ring: 190 72% 40%;"
    },
    "usage": {
      "primary": "CTA buttons, active states, progress, links on hover",
      "accent": "Badges, soft highlights, tab indicators",
      "secondary": "Section backgrounds, cards, tables",
      "muted": "Dividers, subtle surfaces",
      "text": "Foreground on light surfaces always >= 4.5:1 contrast"
    }
  },

  "gradients_and_textures": {
    "restrictions_summary": [
      "NEVER use dark/saturated gradient combos (purple/pink, etc)",
      "Gradients occupy <= 20% viewport and not on text blocks",
      "Do not apply gradients to small UI (<100px width)"
    ],
    "approved_gradients": [
      {
        "name": "Mint-Teal-Sand",
        "css": "bg-[radial-gradient(120%_120%_at_0%_0%,hsl(169_53%_82%)_0%,hsl(190_72%_35%/0.12)_40%,hsl(40_42%_88%)_100%)]"
      },
      {
        "name": "Teal Mist",
        "css": "bg-[linear-gradient(135deg,hsl(190_72%_96%)_0%,hsl(190_72%_90%)_35%,hsl(190_72%_96%)_100%)]"
      }
    ],
    "noise_overlay_css": ".noise::after{content:\"\";position:absolute;inset:0;pointer-events:none;background-image:url('data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'1400\\' height=\\'800\\'><filter id=\\'n\\'><feTurbulence baseFrequency=\\'0.8\\' numOctaves=\\'3\\' stitchTiles=\\'stitch\\'/><feColorMatrix type=\\'saturate\\' values=\\'0\\'/><feComponentTransfer><feFuncA type=\\'table\\' tableValues=\\'0 0.04\\'/></feComponentTransfer></filter><rect width=\\'100%\\' height=\\'100%\\' filter=\\'url(%23n)\\'/></svg>');mix-blend-mode:overlay;opacity:.25}"
  },

  "layout_system": {
    "grid": {
      "container": "mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl",
      "columns": "grid grid-cols-1 md:grid-cols-12 gap-6 md:gap-8",
      "bento": "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6"
    },
    "landing_structure": [
      "Header with logo + CTA",
      "Hero with URL input + live analysis progress",
      "AI Recommendations (bento cards with icons)",
      "Workflow visualization (3-4 steps with connectors)",
      "Trust indicators (logos + short testimonial)",
      "Feature highlights (split + visual)",
      "Pricing CTA",
      "Footer"
    ],
    "dashboard_structure": [
      "Left sidebar nav (icons + labels)",
      "Top bar (search, account menu)",
      "Overview cards (Active automations, Leads captured, Bookings)",
      "Recommendations/Insights (carousel or tabs)",
      "Automation table (status, schedule, last run)",
      "Right drawer/sheet for quick-create"
    ]
  },

  "components": {
    "imports": [
      "import { Button } from \"@/components/ui/button\"",
      "import { Input } from \"@/components/ui/input\"",
      "import { Progress } from \"@/components/ui/progress\"",
      "import { Card, CardHeader, CardContent, CardFooter, CardTitle, CardDescription } from \"@/components/ui/card\"",
      "import { Tabs, TabsList, TabsTrigger, TabsContent } from \"@/components/ui/tabs\"",
      "import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from \"@/components/ui/table\"",
      "import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from \"@/components/ui/tooltip\"",
      "import { Badge } from \"@/components/ui/badge\"",
      "import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from \"@/components/ui/dialog\"",
      "import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from \"@/components/ui/sheet\"",
      "import { Separator } from \"@/components/ui/separator\"",
      "import { Toaster } from \"@/components/ui/sonner\"",
      "import { Switch } from \"@/components/ui/switch\""
    ],
    "icon_library": "lucide-react (preferred) or FontAwesome CDN; never use emoji icons.",
    "button_style": {
      "tone": "Professional/Corporate",
      "shape": "rounded-md via Tailwind radius tokens",
      "motion": "transition-colors duration-300 focus-visible:ring-2 focus-visible:ring-ring",
      "variants": ["primary", "secondary", "ghost"],
      "note": "Avoid transition-all. Add hover:shadow only for larger CTAs."
    },
    "form_fields": {
      "inputs": "Use <Label/> + <Input/> pairs with aria-* attributes and data-testid on both label and input.",
      "progress": "Use <Progress/> for real-time analysis."
    }
  },

  "screens_and_skeletons": {
    "hero_with_url_and_progress.jsx": "import React from 'react'\nimport { useState } from 'react'\nimport { Button } from '@/components/ui/button'\nimport { Input } from '@/components/ui/input'\nimport { Progress } from '@/components/ui/progress'\nimport { motion, useScroll, useTransform } from 'framer-motion'\n\nexport default function Hero() {\n  const [url, setUrl] = useState('')\n  const [progress, setProgress] = useState(0)\n  const [isAnalyzing, setIsAnalyzing] = useState(false)\n\n  const startAnalysis = async () => {\n    setIsAnalyzing(true)\n    setProgress(6)\n    // Simulate streaming progress (replace with WebSocket events)\n    const steps = [18, 32, 55, 72, 89, 100]\n    for (const p of steps) {\n      await new Promise(r => setTimeout(r, 350))\n      setProgress(p)\n    }\n  }\n\n  const { scrollY } = useScroll()\n  const y = useTransform(scrollY, [0, 300], [0, -40])\n\n  return (\n    <section className=\"relative overflow-hidden\">\n      <motion.div style={{ y }} className=\"absolute inset-0 pointer-events-none bg-[radial-gradient(120%_120%_at_0%_0%,hsl(169_53%_82%)_0%,hsl(190_72%_35%/0.10)_40%,hsl(40_42%_88%)_100%)]\"></motion.div>\n      <div className=\"relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16 sm:py-24\">\n        <div className=\"max-w-2xl\">\n          <h1 className=\"font-['Space_Grotesk'] text-4xl sm:text-5xl lg:text-6xl tracking-tight\">Automations from your website — instantly</h1>\n          <p className=\"mt-4 text-sm md:text-base text-muted-foreground max-w-xl\">Paste your URL. We scan your site and propose high-impact automations: chatbots, bookings, lead capture, marketing sequences, and more.</p>\n          <div className=\"mt-6 flex flex-col sm:flex-row gap-3 sm:items-center\">\n            <Input data-testid=\"hero-url-input\" value={url} onChange={e=>setUrl(e.target.value)} placeholder=\"https://yourdomain.com\" className=\"h-12 sm:h-12 sm:min-w-[360px]\"/>\n            <Button data-testid=\"hero-analyze-button\" onClick={startAnalysis} className=\"h-12 px-6\">Analyze URL</Button>\n          </div>\n          {isAnalyzing && (\n            <div className=\"mt-4 space-y-2\">\n              <Progress data-testid=\"hero-analysis-progress\" value={progress} className=\"h-2\"/>\n              <p className=\"text-xs text-muted-foreground\">Scanning sitemap, content, and metadata…</p>\n            </div>\n          )}\n        </div>\n      </div>\n    </section>\n  )\n}",

    "recommendation_card.jsx": "import React from 'react'\nimport { Card, CardHeader, CardContent, CardFooter, CardTitle, CardDescription } from '@/components/ui/card'\nimport { Button } from '@/components/ui/button'\nimport { Badge } from '@/components/ui/badge'\nimport { motion } from 'framer-motion'\n\nexport const RecommendationCard = ({ icon, title, description, ctaLabel='Deploy', onClick }) => {\n  return (\n    <motion.div whileHover={{ y: -3 }} transition={{ type: 'spring', stiffness: 250, damping: 20 }}>\n      <Card data-testid=\"automation-recommendation-card\" className=\"group border-muted bg-card/80 backdrop-blur-sm\">\n        <CardHeader>\n          <div className=\"flex items-center gap-3\">{icon}<CardTitle className=\"text-base\">{title}</CardTitle></div>\n          <CardDescription className=\"text-sm\">{description}</CardDescription>\n        </CardHeader>\n        <CardContent>\n          <Badge className=\"bg-accent text-accent-foreground\">Suggested</Badge>\n        </CardContent>\n        <CardFooter>\n          <Button data-testid=\"automation-deploy-button\" onClick={onClick} className=\"transition-colors duration-300\">{ctaLabel}</Button>\n        </CardFooter>\n      </Card>\n    </motion.div>\n  )\n}\n"
  },

  "dashboard_scaffold.jsx": "import React from 'react'\nimport { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'\nimport { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'\nimport { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/table'\nimport { Button } from '@/components/ui/button'\nimport { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'\nimport { Badge } from '@/components/ui/badge'\n\nexport default function Dashboard() {\n  return (\n    <div className=\"mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8\">\n      <div className=\"grid grid-cols-1 md:grid-cols-12 gap-6\">\n        <div className=\"md:col-span-8 space-y-6\">\n          <div className=\"grid grid-cols-1 sm:grid-cols-3 gap-4\">\n            {[\n              {label:'Active Automations', value: 12},\n              {label:'Leads Captured (30d)', value: 348},\n              {label:'Bookings (30d)', value: 57}\n            ].map((s, i)=> (\n              <Card key={i}>\n                <CardHeader className=\"pb-2\"><CardTitle className=\"text-sm text-muted-foreground\">{s.label}</CardTitle></CardHeader>\n                <CardContent className=\"text-2xl font-semibold\">{s.value}</CardContent>\n              </Card>\n            ))}\n          </div>\n\n          <Tabs defaultValue=\"insights\">\n            <TabsList>\n              <TabsTrigger value=\"insights\">Insights</TabsTrigger>\n              <TabsTrigger value=\"all\">All Automations</TabsTrigger>\n            </TabsList>\n            <TabsContent value=\"insights\">\n              <Card>\n                <CardHeader><CardTitle>Recommended next steps</CardTitle></CardHeader>\n                <CardContent className=\"text-sm text-muted-foreground\">Connect your booking calendar and enable chat widget on 3 high-traffic pages.</CardContent>\n              </Card>\n            </TabsContent>\n            <TabsContent value=\"all\">\n              <Card>\n                <CardHeader><CardTitle>Automations</CardTitle></CardHeader>\n                <CardContent>\n                  <Table>\n                    <TableHeader>\n                      <TableRow>\n                        <TableHead>Name</TableHead>\n                        <TableHead>Type</TableHead>\n                        <TableHead>Status</TableHead>\n                        <TableHead className=\"text-right\">Actions</TableHead>\n                      </TableRow>\n                    </TableHeader>\n                    <TableBody>\n                      {[\n                        {name:'Lead Capture', type:'Form', status:'Active'},\n                        {name:'Bookings', type:'Scheduling', status:'Paused'}\n                      ].map((row,i)=> (\n                        <TableRow key={i} data-testid=\"automation-row\">\n                          <TableCell>{row.name}</TableCell>\n                          <TableCell>{row.type}</TableCell>\n                          <TableCell><Badge variant=\"secondary\">{row.status}</Badge></TableCell>\n                          <TableCell className=\"text-right\">\n                            <Button size=\"sm\" data-testid=\"automation-edit-button\">Edit</Button>\n                          </TableCell>\n                        </TableRow>\n                      ))}\n                    </TableBody>\n                  </Table>\n                </CardContent>\n              </Card>\n            </TabsContent>\n          </Tabs>\n        </div>\n\n        <div className=\"md:col-span-4\">\n          <Sheet>\n            <SheetTrigger asChild>\n              <Button className=\"w-full\" data-testid=\"quick-create-button\">+ Quick Create</Button>\n            </SheetTrigger>\n            <SheetContent side=\"right\">\n              <SheetHeader><SheetTitle>New Automation</SheetTitle></SheetHeader>\n              <div className=\"mt-4 text-sm text-muted-foreground\">Pick a template to start.</div>\n            </SheetContent>\n          </Sheet>\n        </div>\n      </div>\n    </div>\n  )\n}\n",

  "micro_interactions_and_motion": {
    "principles": [
      "Every interactive element has hover and focus-visible states",
      "Use Framer Motion for enter/exit and in-view reveals",
      "No transition-all; prefer transition-colors/opacity/transform specifically"
    ],
    "examples_tailwind": {
      "cta_button": "hover:shadow-md hover:-translate-y-[1px] active:translate-y-0 transition-[box-shadow,transform,background-color,color] duration-300",
      "card_hover": "hover:shadow-sm transition-[box-shadow] duration-300",
      "nav_link": "hover:text-primary transition-colors duration-200"
    },
    "parallax_snippet.jsx": "import { useScroll, useTransform, motion } from 'framer-motion'\nconst Parallax = ({ children }) => {\n  const { scrollY } = useScroll()\n  const y = useTransform(scrollY, [0, 300], [0, -30])\n  return <motion.div style={{ y }}>{children}</motion.div>\n}\nexport default Parallax"
  },

  "accessibility_and_testing": {
    "a11y": [
      "Maintain 4.5:1 contrast for text vs background",
      "Use semantic HTML with labels for all form controls",
      "Provide focus-visible rings with sufficient contrast",
      "Respect prefers-reduced-motion; reduce motion intensity accordingly"
    ],
    "data_testid_policy": {
      "requirement": "All interactive and key informational elements MUST include data-testid using kebab-case, role-oriented names.",
      "examples": [
        "data-testid=\"hero-url-input\"",
        "data-testid=\"hero-analyze-button\"",
        "data-testid=\"hero-analysis-progress\"",
        "data-testid=\"automation-recommendation-card\"",
        "data-testid=\"automation-deploy-button\"",
        "data-testid=\"automation-row\"",
        "data-testid=\"quick-create-button\""
      ]
    }
  },

  "trust_and_social_proof": {
    "logos_row": "Place 4-6 monochrome brand logos in a muted row below hero input using grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-6 items-center opacity-70",
    "testimonial_card": "Use Card with quote, small avatar, name, role. Keep contrast high and copy short."
  },

  "workflow_visualization": {
    "pattern": "3-4 steps in a horizontal scroll on mobile, connected by soft dotted lines on md+ using CSS background or SVG. Colors: active=primary, upcoming=muted-foreground.",
    "technique": "Use framer-motion whileInView to stagger step reveal and a Progress to animate step completion."
  },

  "image_urls": [
    {
      "url": "https://images.unsplash.com/photo-1664526937033-fe2c11f1be25?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwxfHxhYnN0cmFjdCUyMG5ldHdvcmslMjBub2RlcyUyMGxpbmVzJTIwc29mdCUyMHRlYWwlMjBtaW50JTIwYmFja2dyb3VuZHxlbnwwfHx8dGVhbHwxNzYyMDQ2MTA3fDA&ixlib=rb-4.1.0&q=85",
      "category": "decorative_hero_backdrop",
      "description": "Abstract network diagram; use as subtle overlay behind the hero input."
    },
    {
      "url": "https://images.unsplash.com/photo-1552332271-bf8afb3d4596?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwyfHxhYnN0cmFjdCUyMG5ldHdvcmslMjBub2RlcyUyMGxpbmVzJTIwc29mdCUyMHRlYWwlMjBtaW50JTIwYmFja2dyb3VuZHxlbnwwfHx8dGVhbHwxNzYyMDQ2MTA3fDA&ixlib=rb-4.1.0&q=85",
      "category": "texture",
      "description": "Soft teal starry texture; apply in sections sparingly (opacity < 0.15)."
    },
    {
      "url": "https://images.unsplash.com/photo-1569970256965-3f869284ab64?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwzfHxhYnN0cmFjdCUyMG5ldHdvcmslMjBub2RlcyUyMGxpbmVzJTIwc29mdCUyMHRlYWwlMjBtaW50JTIwYmFja2dyb3VuZHxlbnwwfHx8dGVhbHwxNzYyMDQ2MTA3fDA&ixlib=rb-4.1.0&q=85",
      "category": "section_divider",
      "description": "Turquoise crackle pattern; use as a faint divider background on wide sections."
    }
  ],

  "component_path": {
    "button": "/app/frontend/src/components/ui/button.jsx",
    "input": "/app/frontend/src/components/ui/input.jsx",
    "progress": "/app/frontend/src/components/ui/progress.jsx",
    "card": "/app/frontend/src/components/ui/card.jsx",
    "tabs": "/app/frontend/src/components/ui/tabs.jsx",
    "table": "/app/frontend/src/components/ui/table.jsx",
    "dialog": "/app/frontend/src/components/ui/dialog.jsx",
    "tooltip": "/app/frontend/src/components/ui/tooltip.jsx",
    "badge": "/app/frontend/src/components/ui/badge.jsx",
    "sheet": "/app/frontend/src/components/ui/sheet.jsx",
    "separator": "/app/frontend/src/components/ui/separator.jsx",
    "sonner_toaster": "/app/frontend/src/components/ui/sonner.jsx",
    "switch": "/app/frontend/src/components/ui/switch.jsx",
    "calendar": "/app/frontend/src/components/ui/calendar.jsx"
  },

  "patterns_and_pages": {
    "landing_hero": {
      "layout_classes": "mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16 sm:py-24",
      "interaction": "Parallax background, input + analyze button, progress appears after click"
    },
    "ai_recommendations": {
      "layout_classes": "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6",
      "cards": "Use RecommendationCard with lucide icons and Deploy CTA"
    },
    "trust_indicators": {
      "layout_classes": "mt-10 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-6 items-center opacity-70"
    },
    "dashboard_overview": {
      "layout_classes": "grid grid-cols-1 md:grid-cols-12 gap-6",
      "cards": "3 stat cards, tabs for insights and all automations, table for details"
    }
  },

  "extra_libraries": {
    "framer_motion": {
      "install": "npm i framer-motion",
      "usage": "Animate hero backdrop, card hover, and in-view reveals"
    },
    "recharts": {
      "install": "npm i recharts",
      "usage": "KPIs and sparkline charts inside cards (LineChart/AreaChart). Keep colors in brand palette."
    },
    "lottie": {
      "install": "npm i lottie-react",
      "usage": "Optional: small looping automation illustration in hero (opacity <= .8). Provide video/gif fallback."
    }
  },

  "forms_and_feedback": {
    "toasts": "Use sonner (components/ui/sonner.jsx). Example: import { toast } from 'sonner'; toast.success('Automation deployed');",
    "empty_states": "Use icons + one action. Copy is concise and encouraging."
  },

  "content_style": {
    "headlines": "Benefit-led, concise, verbs up front",
    "subcopy": "Short, skimmable lines; one idea per sentence",
    "cta_labels": ["Analyze URL", "Deploy", "Enable", "Connect", "Start Free"]
  },

  "do_and_dont_specific": {
    "do": [
      "Use more whitespace than you think",
      "Keep hero highly focused on the URL input",
      "Use parallax & subtle noise to avoid flatness",
      "Prefer solid backgrounds for content blocks"
    ],
    "dont": [
      "No purple/pink dark gradients",
      "No universal transition-all",
      "No centered .App container styles",
      "No emojis for icons"
    ]
  },

  "instructions_to_main_agent": [
    "1) Update /app/frontend/src/index.css tokens with color_system.css_tokens_override_for_index_css and dark_mode_tokens",
    "2) Build Hero component from screens_and_skeletons.hero_with_url_and_progress.jsx and place on Landing page",
    "3) Implement AI Recommendations grid using RecommendationCard (wire icons via lucide-react)",
    "4) Add trust logos row and a short testimonial card",
    "5) Create Dashboard page using dashboard_scaffold.jsx; connect data later to FastAPI",
    "6) Add micro interactions from micro_interactions_and_motion and ensure prefers-reduced-motion is respected",
    "7) Ensure all interactive elements include data-testid per policy",
    "8) Add Toaster provider at app root and use sonner for success/error",
    "9) If calendar is required, use shadcn calendar component only",
    "10) Keep gradients limited to hero/section backgrounds; use solid colors in content blocks"
  ],

  "general_ui_ux_design_guidelines": "- You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms\n- You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text\n- NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json\n\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**\n\n</Font Guidelines>\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. \n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts"  
}


<General UI UX Design Guidelines>  
    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms
    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text
   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json

 **GRADIENT RESTRICTION RULE**
NEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc
NEVER use dark gradients for logo, testimonial, footer etc
NEVER let gradients cover more than 20% of the viewport.
NEVER apply gradients to text-heavy content or reading areas.
NEVER use gradients on small UI elements (<100px width).
NEVER stack multiple gradient layers in the same viewport.

**ENFORCEMENT RULE:**
    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors

**How and where to use:**
   • Section backgrounds (not content backgrounds)
   • Hero section header content. Eg: dark to light to dark color
   • Decorative overlays and accent elements only
   • Hero section with 2-3 mild color
   • Gradients creation can be done for any angle say horizontal, vertical or diagonal

- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**

</Font Guidelines>

- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. 
   
- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.

- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.
   
- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly
    Eg: - if it implies playful/energetic, choose a colorful scheme
           - if it implies monochrome/minimal, choose a black–white/neutral scheme

**Component Reuse:**
	- Prioritize using pre-existing components from src/components/ui when applicable
	- Create new components that match the style and conventions of existing components when needed
	- Examine existing components to understand the project's component patterns before creating new ones

**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component

**Best Practices:**
	- Use Shadcn/UI as the primary component library for consistency and accessibility
	- Import path: ./components/[component-name]

**Export Conventions:**
	- Components MUST use named exports (export const ComponentName = ...)
	- Pages MUST use default exports (export default function PageName() {...})

**Toasts:**
  - Use `sonner` for toasts"
}