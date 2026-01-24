import { useRef, useEffect, useCallback} from 'react';
import "./loadBar.scss"

interface ILoadBar{
    className?: string
}

interface Point {
  x: number;
  y: number;
  vx: number;
  vy: number;
  buddy?: Point;
}

const DrowData = {
    width: 200, 
    height: 200, 
    numberOfPoints: 30,
    velocity: 5,
    pointRadius: 5,
    pointColor: '#97badc',
    lineColor: '#8ab2d8',
    backgroundColor: '#102131',
    rotate: 45 
}

export const LoadBar = (props: ILoadBar) =>{
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const animationRef = useRef<number | null>(null);
    const pointsRef = useRef<Point[]>([]);

    const initPoints = useCallback((): Point[] => {
        const points: Point[] = [];
    
        for (let i = 0; i < DrowData.numberOfPoints; i++) {
        const vx = (Math.floor(Math.random()) * 2 - 1) * Math.random();
        const vx2 = Math.pow(vx, 2);
        const vy2 = DrowData.velocity - vx2;
        const vy = Math.sqrt(vy2) * (Math.random() * 2 - 1);
        
        points.push({
            x: Math.random() * DrowData.width,
            y: Math.random() * DrowData.height,
            vx,
            vy
        });
        }

        points.forEach((point, index) => {
        point.buddy = index === 0 ? points[points.length - 1] : points[index - 1];
        });

        return points;
    }, [DrowData.width, DrowData.height, DrowData.numberOfPoints, DrowData.velocity]);

  const animate = useCallback(() => {
        const canvas = canvasRef.current;
        const context = canvas?.getContext('2d');
        if (!context) return;

        context.clearRect(0, 0, DrowData.width, DrowData.height);

        pointsRef.current.forEach((point) => {
        point.x += point.vx;
        point.y += point.vy;

        // Границы
        if (point.x <= DrowData.pointRadius || point.x >= DrowData.width - DrowData.pointRadius) {
            point.vx *= -1;
        }
        if (point.y <= DrowData.pointRadius || point.y >= DrowData.height - DrowData.pointRadius) {
            point.vy *= -1;
        }

        // Отрисовка
        if (point.buddy) {
            context.beginPath();
            context.arc(point.x, point.y, DrowData.pointRadius, 0, 2 * Math.PI);
            context.fillStyle = DrowData.pointColor;
            context.fill();

            context.beginPath();
            context.moveTo(point.x, point.y);
            context.lineTo(point.buddy.x, point.buddy.y);
            context.strokeStyle = DrowData.lineColor;
            context.stroke();
        }
        });

        animationRef.current = requestAnimationFrame(animate);
    }, [DrowData.width, DrowData.height, DrowData.pointRadius, DrowData.pointColor, DrowData.lineColor]);

    const start = useCallback(() => {
        if (!animationRef.current) {
            pointsRef.current = initPoints();
            animate();
        }
    }, [initPoints, animate]);

    const stop = useCallback(() => {
        if (animationRef.current) {
            cancelAnimationFrame(animationRef.current); 
            animationRef.current = null;
        }
    }, []);

    useEffect(() => {
        start()
        return () => stop();
    }, [stop]);


    return (
        <div className={props.className ? `${props.className} ai-center`: "ai-center"}>
            <div className="flex jc-center ai-center fd-column">
               
                <canvas
                    ref={canvasRef}
                    width={DrowData.width}
                    height={DrowData.height}
                    className="load-bar-canvas"
                    id="load-container"
                    // style={{ transform: `rotate(${DrowData.rotate}deg)` }}
                />
                <p>Подождите пожалуйста, мы усердно считаем, это может занять какое-то время</p>
                {/* <canvas id="load-container" width="200" height="200"></canvas> */}
            </div>
            
        </div>
    )
}