"use client";
import { signup } from "@/lib/api";
import { useState } from "react";
import { motion } from "framer-motion";
import { User, Mail, Lock, ArrowRight, Target } from "lucide-react";
import Link from "next/link";
export default function SignUpPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("");
  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const data = await signup(email, password, role);

      alert("Account created successfully");

      window.location.href = "/login";
    } catch (err) {
      console.error(err);
    }
  };
  return (
    <div
      className="flex items-center justify-center 
min-h-[80vh]"
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        // transition={{ duration: 0.5 }}
        className="w-full max-w-md glass-panel p-8 
rounded-3xl relative overflow-hidden group"
        whileHover={{
          rotateX: 8,
          rotateY: -8,
          scale: 1.03,
        }}
        transition={{ type: "spring", stiffness: 200 }}
        style={{
          transformStyle: "preserve-3d",
        }}
      >
        <div
          className="absolute -inset-10 bg-primary/
5 blur-2xl transition-colors -z-10"
        />
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="w-16 h-16 mx-auto bg-primary/10 
rounded-full flex items-center justify-center 
mb-4"
          >
            <Target className="w-8 h-8 text-primary" />
          </motion.div>
          <h1
            className="text-3xl font-bold tracking-tight 
text-transparent bg-clip-text bg-gradient-to-r 
from-white to-gray-400"
          >
            Join{" "}
            <span
              className="text
primary"
            >
              CareerAI
            </span>
          </h1>
          <p
            className="text-muted-foreground 
mt-2"
          >
            Start your intelligent career progression.
          </p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-background/50 border 
border-border/50 rounded-xl py-3 pl-12 pr-4 text
foreground focus:outline-none focus:border
primary/50 focus:ring-1 focus:ring-primary/50 
transition-all placeholder:text-muted-foreground"
                required
              />
            </div>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="email"
                placeholder="Email Address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-background/50 border 
border-border/50 rounded-xl py-3 pl-12 pr-4 text
foreground focus:outline-none focus:border
primary/50 focus:ring-1 focus:ring-primary/50 
transition-all placeholder:text-muted-foreground"
                required
              />
            </div>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-background/50 border 
border-border/50 rounded-xl py-3 pl-12 pr-4 text
foreground focus:outline-none focus:border
primary/50 focus:ring-1 focus:ring-primary/50 
transition-all placeholder:text-muted-foreground"
                required
              />
            </div>
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-background/50 border 
border-border/50 rounded-xl py-3 pl-12 pr-4 text
foreground focus:outline-none focus:border
primary/50 focus:ring-1 focus:ring-primary/50 
transition-all placeholder:text-muted-foreground"
                required
              />
            </div>
          </div>
          <button
            type="submit"
            className="w-full bg-primary text-primary
foreground font-semibold py-3 rounded-xl flex 
items-center justify-center space-x-2 hover:bg
primary/90 transition-colors group"
          >
            <span
              style={{
                color: "white",
              }}
            >
              Create Profile
            </span>
            <ArrowRight
              className="w-5 h-5 group
hover:translate-x-1 transition-transform"
            />
          </button>
        </form>
        <p
          className="text-center mt-8 text-sm text
muted-foreground"
        >
          Already have an account?{" "}
          <Link
            href="/login"
            className="text-primary 
font-medium hover:text-primary/80 transition
colors"
          >
            Sign In
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
