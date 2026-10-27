import { Canvas, useFrame } from "@react-three/fiber";
import { useEffect, useRef, useState, useMemo } from "react";
import AvatarManager from "@/class/AvatarManager";
import { OrbitControls, Float, Text3D } from "@react-three/drei";
import audioBlendShapes from "../../blendshapes.json";

// ---------------------------------------------------------------
// Types
// ---------------------------------------------------------------
interface BlendShapeData {
  categoryName: string;
  score: number;
}

interface AvatarCanvasProps {
  width: number;
  height: number;
  url: string;
}

interface AvatarSceneProps {
  url: string;
  isPlaying: boolean;
  audioRef: React.MutableRefObject<HTMLAudioElement | null>;
  progressBarRef: React.MutableRefObject<HTMLDivElement | null>;
  onLoaded: () => void;
  setIsPlaying: (val: boolean) => void;
}

const FPS = 30;

// ---------------------------------------------------------------
// Math Helper: Linear Interpolation
// ---------------------------------------------------------------
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// ---------------------------------------------------------------
// Blendshape Interpolation
// ---------------------------------------------------------------
const applyBlendshapesInterp = (
  avatarManager: any,
  prevFrame: BlendShapeData[],
  nextFrame: BlendShapeData[] | undefined,
  alpha: number
) => {
  if (!avatarManager || !prevFrame || prevFrame.length === 0) {
    console.warn("Invalid frame data or avatarManager");
    return;
  }

  const finalFrame = nextFrame || prevFrame;

  const blended = prevFrame.map((item, i) => {
    const nextScore = finalFrame[i]?.score ?? item.score;
    return {
      categoryName: item.categoryName,
      score: lerp(item.score, nextScore, alpha),
    };
  });

  const data = {
    faceLandmarks: [[]],
    faceBlendshapes: [
      {
        categories: blended,
        headIndex: 0,
        headName: "head",
      },
    ],
    facialTransformationMatrixes: [],
  };

  try {
    avatarManager.updateFacialTransforms(data, true);
  } catch (error) {
    console.error("Error updating facial transforms:", error);
  }
};

// ---------------------------------------------------------------
// Scene Component
// ---------------------------------------------------------------
const AvatarScene = ({
  url,
  isPlaying,
  audioRef,
  progressBarRef,
  onLoaded,
  setIsPlaying,
}: AvatarSceneProps) => {
  const [scene, setScene] = useState<THREE.Scene | null>(null);
  const avatarManager = useMemo(() => AvatarManager.getInstance(), []);

  // Load the model
  useEffect(() => {
    let mounted = true;

    avatarManager.loadModel(url).then(() => {
      if (!mounted) return;

      setScene(avatarManager.getScene());
      onLoaded();

      // Verify data structure
      console.log("Total frames:", audioBlendShapes.length);
      console.log("First frame structure:", audioBlendShapes[0]);
      console.log("First frame is array?", Array.isArray(audioBlendShapes[0]));
      
      // Access the first frame correctly - it's an array of arrays
      const firstFrame = Array.isArray(audioBlendShapes[0][0]) 
        ? audioBlendShapes[0][0] 
        : audioBlendShapes[0];
      
      console.log("Applying first frame:", firstFrame);
      console.log("Number of blendshapes:", firstFrame?.length);

      // Apply frame 0 instantly
      if (firstFrame) {
        applyBlendshapesInterp(
          avatarManager,
          firstFrame,
          firstFrame,
          0
        );
      }

      // Auto play audio
      audioRef.current?.play().then(() => {
        setIsPlaying(true);
      }).catch(err => {
        console.error("Audio play failed:", err);
      });
    }).catch(err => {
      console.error("Model loading failed:", err);
    });

    return () => {
      mounted = false;
    };
  }, [url, avatarManager, audioRef, onLoaded, setIsPlaying]);

  // Animation Loop
  useFrame(() => {
    if (!audioRef.current || !scene) return;

    const audio = audioRef.current;

    // Update progress bar
    if (progressBarRef.current && audio.duration > 0) {
      const pct = (audio.currentTime / audio.duration) * 100;
      progressBarRef.current.style.width = `${pct}%`;
    }

    // Don't animate if not playing
    if (!isPlaying) return;

    const exactFrame = audio.currentTime * FPS;
    const frameIndex = Math.floor(exactFrame);
    const alpha = exactFrame - frameIndex;

    if (frameIndex < 0 || frameIndex >= audioBlendShapes.length) return;

    // Access frames correctly - handle nested array structure
    const currentFrameData = audioBlendShapes[frameIndex];
    const nextFrameData = audioBlendShapes[frameIndex + 1];

    // Extract the actual blend shape array (it's nested)
    const prevFrame = Array.isArray(currentFrameData[0]) 
      ? currentFrameData[0] 
      : currentFrameData;
    
    const nextFrame = nextFrameData 
      ? (Array.isArray(nextFrameData[0]) ? nextFrameData[0] : nextFrameData)
      : undefined;

    // Debug first few frames
    if (frameIndex < 3) {
      console.log(`Frame ${frameIndex}, alpha: ${alpha.toFixed(2)}`);
    }

    applyBlendshapesInterp(avatarManager, prevFrame, nextFrame, alpha);
  });

  return (
    <>
      <ambientLight intensity={0.6} />
      <directionalLight position={[5, 5, 5]} />

      {scene && <primitive object={scene} />}
    </>
  );
};

// ---------------------------------------------------------------
// Main Canvas Wrapper
// ---------------------------------------------------------------
const AvatarCanvas = ({ width, height, url }: AvatarCanvasProps) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const progressBarRef = useRef<HTMLDivElement | null>(null);

  // Create audio
  useEffect(() => {
    const audio = new Audio("/harvard.wav");
    audioRef.current = audio;

    const handleEnded = () => setIsPlaying(false);
    const handleLoadedMetadata = () => {
      console.log("Audio loaded, duration:", audio.duration);
      console.log("Expected frames:", Math.floor(audio.duration * FPS));
    };

    audio.addEventListener("ended", handleEnded);
    audio.addEventListener("loadedmetadata", handleLoadedMetadata);

    return () => {
      audio.pause();
      audio.removeEventListener("ended", handleEnded);
      audio.removeEventListener("loadedmetadata", handleLoadedMetadata);
    };
  }, []);

  const togglePlay = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().then(() => {
        setIsPlaying(true);
      }).catch(err => {
        console.error("Play failed:", err);
      });
    }
  };

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current;
    if (!audio) return;

    // Avoid setting currentTime while metadata is not ready
    if (!isLoaded || !isFinite(audio.duration) || audio.duration === 0) {
      console.warn("Audio not ready for seeking");
      return;
    }

    const rect = e.currentTarget.getBoundingClientRect();
    let percent = (e.clientX - rect.left) / rect.width;

    // Clamp 0–1
    percent = Math.min(1, Math.max(0, percent));

    const newTime = percent * audio.duration;

    // Additional guard: avoid NaN
    if (!isFinite(newTime)) {
      console.warn("Computed seek time is invalid:", newTime);
      return;
    }

    audio.currentTime = newTime;

    // Apply correct frame instantly (even when paused)
    const f = newTime * FPS;
    const idx = Math.floor(f);
    const alpha = f - idx;

    if (idx >= 0 && idx < audioBlendShapes.length) {
      const currentFrameData = audioBlendShapes[idx];
      const nextFrameData = audioBlendShapes[idx + 1];
      
      const prevFrame = Array.isArray(currentFrameData[0]) 
        ? currentFrameData[0] 
        : currentFrameData;
      
      const nextFrame = nextFrameData 
        ? (Array.isArray(nextFrameData[0]) ? nextFrameData[0] : nextFrameData)
        : undefined;

      applyBlendshapesInterp(
        AvatarManager.getInstance(),
        prevFrame,
        nextFrame,
        alpha
      );
    }
  };

  return (
    <div className="relative bg-black overflow-hidden" style={{ width, height }}>
      <Canvas camera={{ fov: 30, position: [0, 0.5, 1] }}>
        <OrbitControls enablePan={false} enableZoom={false} target={[0, 0.6, 0]} />

        <AvatarScene
          url={url}
          isPlaying={isPlaying}
          setIsPlaying={setIsPlaying}
          audioRef={audioRef}
          progressBarRef={progressBarRef}
          onLoaded={() => setIsLoaded(true)}
        />

        {!isLoaded && (
          <Float>
            <Text3D
              font="../assets/fonts/Open_Sans_Condensed_Bold.json"
              scale={0.05}
              position={[-0.15, 0.6, 0]}
            >
              Loading...
              <meshNormalMaterial />
            </Text3D>
          </Float>
        )}
      </Canvas>

      {/* UI Layer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/90 to-transparent">

        {/* Progress Bar */}
        <div className="w-full h-2 bg-gray-700 rounded-full mb-4 cursor-pointer" onClick={handleSeek}>
          <div
            ref={progressBarRef}
            className="h-full bg-blue-500 rounded-full transition-all"
            style={{ width: "0%" }}
          />
        </div>

        {/* Play Button */}
        <div className="flex justify-center">
          <button
            onClick={togglePlay}
            className="w-12 h-12 rounded-full bg-blue-600 text-white flex items-center justify-center hover:bg-blue-500"
          >
            {isPlaying ? (
              <div className="flex gap-1">
                <div className="w-2 h-6 bg-white" />
                <div className="w-2 h-6 bg-white" />
              </div>
            ) : (
              <div className="ml-1 w-0 h-0 border-t-[12px] border-b-[12px] border-l-[20px] border-t-transparent border-b-transparent border-l-white" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AvatarCanvas;