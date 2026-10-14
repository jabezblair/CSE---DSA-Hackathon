import java.io.*;
import java.util.*;
import java.util.concurrent.ThreadLocalRandom;

public class ClosestPair {

    static double dist2(double[] a, double[] b) {
        double dx = a[0] - b[0], dy = a[1] - b[1];
        return dx * dx + dy * dy;
    }

    static double[] bruteForce(double[][] pts) {
        int n = pts.length;
        double best = Double.POSITIVE_INFINITY;
        double[] pair = null;
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++) {
                double d = dist2(pts[i], pts[j]);
                if (d < best) {
                    best = d;
                    pair = new double[]{pts[i][0], pts[i][1], pts[j][0], pts[j][1]};
                }
            }
        if (pair == null) return new double[]{Double.POSITIVE_INFINITY};
        return new double[]{Math.sqrt(best), pair[0], pair[1], pair[2], pair[3]};
    }

    // ---------- Divide and Conquer ----------

    static double bestDist;
    static double[] bestPair;

    static double[] closestPair(double[][] pts) {
        int n = pts.length;
        if (n < 2) return new double[]{Double.POSITIVE_INFINITY};
        Integer[] idx = new Integer[n];
        for (int i = 0; i < n; i++) idx[i] = i;
        Arrays.sort(idx, (a, b) -> {
            if (pts[a][0] != pts[b][0]) return Double.compare(pts[a][0], pts[b][0]);
            return Double.compare(pts[a][1], pts[b][1]);
        });
        bestDist = Double.POSITIVE_INFINITY;
        bestPair = null;
        rec(pts, idx, 0, n);
        return new double[]{Math.sqrt(bestDist), bestPair[0], bestPair[1], bestPair[2], bestPair[3]};
    }

    static void rec(double[][] pts, Integer[] ix, int lo, int hi) {
        int m = hi - lo;
        if (m <= 3) {
            for (int a = lo; a < hi; a++)
                for (int b = a + 1; b < hi; b++) {
                    double d = dist2(pts[ix[a]], pts[ix[b]]);
                    if (d < bestDist) {
                        bestDist = d;
                        bestPair = new double[]{pts[ix[a]][0], pts[ix[a]][1], pts[ix[b]][0], pts[ix[b]][1]};
                    }
                }
            return;
        }
        int mid = lo + m / 2;
        double midX = pts[ix[mid]][0];
        rec(pts, ix, lo, mid);
        rec(pts, ix, mid, hi);

        List<Integer> strip = new ArrayList<>();
        for (int i = lo; i < hi; i++) {
            double dx = pts[ix[i]][0] - midX;
            if (dx * dx < bestDist) strip.add(ix[i]);
        }
        strip.sort(Comparator.comparingDouble(i -> pts[i][1]));
        for (int a = 0; a < strip.size(); a++) {
            for (int b = a + 1; b < Math.min(a + 8, strip.size()); b++) {
                int i = strip.get(a), j = strip.get(b);
                double d = dist2(pts[i], pts[j]);
                if (d < bestDist) {
                    bestDist = d;
                    bestPair = new double[]{pts[i][0], pts[i][1], pts[j][0], pts[j][1]};
                }
            }
        }
    }

    public static void main(String[] args) throws IOException {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 200;
        int seed = args.length > 1 ? Integer.parseInt(args[1]) : 7;
        Random r = new Random(seed);
        double[][] pts = new double[n][2];
        try (PrintWriter pw = new PrintWriter("points.csv")) {
            for (int i = 0; i < n; i++) {
                pts[i][0] = r.nextDouble() * 1000;
                pts[i][1] = r.nextDouble() * 1000;
                pw.printf("%f,%f%n", pts[i][0], pts[i][1]);
            }
        }

        if (n < 2) {
            System.out.println("Brute-Force : inf (N<2)");
            System.out.println("Divide&Conq : inf (N<2)");
            return;
        }

        long t0 = System.nanoTime();
        double[] bf = bruteForce(pts);
        long t1 = System.nanoTime();
        double[] dc = closestPair(pts);
        long t2 = System.nanoTime();

        System.out.printf("Brute-Force : %.6f  (%.2f,%.2f) (%.2f,%.2f)  time=%.3f ms%n",
                bf[0], bf[1], bf[2], bf[3], bf[4], (t1 - t0) / 1e6);
        System.out.printf("Divide&Conq : %.6f  (%.2f,%.2f) (%.2f,%.2f)  time=%.3f ms%n",
                dc[0], dc[1], dc[2], dc[3], dc[4], (t2 - t1) / 1e6);
        System.out.println("Agree: " + (Math.abs(bf[0] - dc[0]) < 1e-9));
    }
}