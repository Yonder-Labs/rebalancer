#!/usr/bin/env node

// Choose imports based on environment

// Option 1
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import crypto from 'crypto';
import { execSync } from 'child_process';
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Option 2
// const fs = require('fs');
// const path = require('path');
// const { execSync } = require('child_process');
// const crypto = require('crypto');

// ============================================================================
// CONFIGURATION: Load licensing configuration from JSON file
// ============================================================================
const configPath = path.join(__dirname, 'licensing-config.json');
if (!fs.existsSync(configPath)) {
  console.error(`❌ Error: licensing-config.json not found at ${configPath}`);
  process.exit(1);
}

const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
const LICENSES_TO_INCLUDE = config.licensesToInclude;
const LICENSE_VARIATIONS = config.licenseVariations;
const allowLicenses = config.categorization.allowLicenses;
const reviewRequiredLicenses = config.categorization.reviewRequiredLicenses;
const counselRequiredLicenses = config.categorization.counselRequiredLicenses;

// ============================================================================
// Configuration loaded from licensing-config.json above
// ============================================================================

console.log('🔍 Scanning repository for package.json, Cargo.toml, and Python project files...\n');

// Find all package.json, Cargo.toml, and Python project files
const findFiles = (dir, pattern, results = []) => {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      // Skip node_modules, target, and other build directories
      if (!['node_modules', 'target', '.git', 'dist', 'build', '__pycache__', '.venv', 'venv', '.env'].includes(entry.name)) {
        findFiles(fullPath, pattern, results);
      }
    } else if (entry.name === pattern) {
      results.push(fullPath);
    }
  }
  return results;
};

const packageJsonFiles = findFiles(process.cwd(), 'package.json');
const cargoTomlFiles = findFiles(process.cwd(), 'Cargo.toml');
const pyprojectTomlFiles = findFiles(process.cwd(), 'pyproject.toml');

// Check for unsupported Python project files and error if found
const requirementsTxtFiles = findFiles(process.cwd(), 'requirements.txt');
const setupPyFiles = findFiles(process.cwd(), 'setup.py');
const pipfileFiles = findFiles(process.cwd(), 'Pipfile');
const poetryLockFiles = findFiles(process.cwd(), 'poetry.lock');
const pipfileLockFiles = findFiles(process.cwd(), 'Pipfile.lock');

if (requirementsTxtFiles.length > 0) {
  console.error(`❌ Error: requirements.txt files are not supported. Only pyproject.toml (PEP 621) is supported.`);
  console.error(`   Found: ${requirementsTxtFiles.join(', ')}`);
  process.exit(1);
}

if (setupPyFiles.length > 0) {
  console.error(`❌ Error: setup.py files are not supported. Only pyproject.toml (PEP 621) is supported.`);
  console.error(`   Found: ${setupPyFiles.join(', ')}`);
  process.exit(1);
}

if (pipfileFiles.length > 0) {
  console.error(`❌ Error: Pipfile files are not supported. Only pyproject.toml (PEP 621) is supported.`);
  console.error(`   Found: ${pipfileFiles.join(', ')}`);
  process.exit(1);
}

if (pipfileLockFiles.length > 0) {
  console.error(`❌ Error: Pipfile.lock files are not supported. Only pyproject.toml (PEP 621) is supported.`);
  console.error(`   Found: ${pipfileLockFiles.join(', ')}`);
  process.exit(1);
}

if (poetryLockFiles.length > 0) {
  console.error(`❌ Error: poetry.lock files are not supported. Only pyproject.toml (PEP 621) is supported.`);
  console.error(`   Found: ${poetryLockFiles.join(', ')}`);
  process.exit(1);
}

// Check pyproject.toml files for Poetry projects
for (const pyprojectToml of pyprojectTomlFiles) {
  try {
    const content = fs.readFileSync(pyprojectToml, 'utf8');
    if (content.includes('[tool.poetry]')) {
      console.error(`❌ Error: Poetry projects are not supported. Only standard pyproject.toml (PEP 621) is supported.`);
      console.error(`   Found Poetry project: ${pyprojectToml}`);
      console.error(`   Please use standard [project] section instead of [tool.poetry]`);
      process.exit(1);
    }
  } catch (e) {
    console.error(`❌ Error: Could not read ${pyprojectToml}: ${e.message}`);
    process.exit(1);
  }
}

// Group Python projects by directory (only pyproject.toml supported)
const pythonProjects = new Map();
pyprojectTomlFiles.forEach(file => {
  const dir = path.dirname(file);
  if (!pythonProjects.has(dir)) {
    pythonProjects.set(dir, {
      dir: dir,
      pyprojectToml: file
    });
  }
});
const pythonProjectDirs = Array.from(pythonProjects.values());

console.log(`Found ${packageJsonFiles.length} package.json file(s):`);
packageJsonFiles.forEach(f => console.log(`  - ${f}`));
console.log(`\nFound ${cargoTomlFiles.length} Cargo.toml file(s):`);
cargoTomlFiles.forEach(f => console.log(`  - ${f}`));
console.log(`\nFound ${pythonProjectDirs.length} Python project(s) (pyproject.toml only):`);
pythonProjectDirs.forEach(proj => {
  console.log(`  - ${proj.dir} (pyproject.toml)`);
});
console.log('\n');

// Install dependencies
console.log('📥 Installing dependencies...\n');

// Install NPM dependencies
for (const pkgJsonPath of packageJsonFiles) {
  const dir = path.dirname(pkgJsonPath);
  console.log(`📦 Installing npm dependencies for ${pkgJsonPath}...`);
  try {
    execSync(`cd "${dir}" && npm install`, {
      stdio: 'inherit'
    });
    console.log(`  ✓ Dependencies installed\n`);
  } catch (error) {
    console.log(`  ⚠ Warning: Failed to install dependencies for ${pkgJsonPath}\n`);
  }
}

// Install Cargo dependencies
for (const cargoTomlPath of cargoTomlFiles) {
  const dir = path.dirname(cargoTomlPath);
  console.log(`🦀 Fetching cargo dependencies for ${cargoTomlPath}...`);
  try {
    execSync(`cd "${dir}" && cargo fetch`, {
      stdio: 'inherit'
    });
    console.log(`  ✓ Dependencies fetched\n`);
  } catch (error) {
    console.log(`  ⚠ Warning: Failed to fetch dependencies for ${cargoTomlPath}\n`);
  }
}

// Install Python dependencies (only for pyproject.toml projects)
for (const pythonProject of pythonProjectDirs) {
  const dir = pythonProject.dir;
  
  console.log(`🐍 Installing Python dependencies for ${dir}...`);
  try {
    // Install project with pyproject.toml (PEP 621)
    execSync(`cd "${dir}" && pip install -e .`, {
      stdio: 'inherit'
    });
    console.log(`  ✓ Dependencies installed\n`);
  } catch (error) {
    console.log(`  ⚠ Warning: Failed to install dependencies for ${dir} (will still attempt SBOM generation)\n`);
  }
}

console.log('🔨 Generating SBOMs...\n');

// Generate SBOMs
const sbomFiles = [];
const tempDir = path.join(process.cwd(), '.sbom-temp');
if (!fs.existsSync(tempDir)) {
  fs.mkdirSync(tempDir);
}

// Generate NPM SBOMs
for (let i = 0; i < packageJsonFiles.length; i++) {
  const pkgJsonPath = packageJsonFiles[i];
  const dir = path.dirname(pkgJsonPath);
  const sbomFile = path.join(tempDir, `sbom-npm-${i}.json`);
  
  console.log(`📦 Generating SBOM for ${pkgJsonPath}...`);
  try {
    execSync(`cd "${dir}" && cyclonedx-npm --output-file "${sbomFile}" --ignore-npm-errors`, {
      stdio: 'inherit'
    });
    if (fs.existsSync(sbomFile)) {
      sbomFiles.push(sbomFile);
      console.log(`  ✓ Generated: ${sbomFile}\n`);
    }
  } catch (error) {
    console.log(`  ⚠ Warning: Failed to generate SBOM for ${pkgJsonPath}\n`);
  }
}

// Generate Cargo SBOMs
for (let i = 0; i < cargoTomlFiles.length; i++) {
  const cargoTomlPath = cargoTomlFiles[i];
  const dir = path.dirname(cargoTomlPath);
  const sbomFile = path.join(tempDir, `sbom-cargo-${i}.json`);
  
  console.log(`🦀 Generating SBOM for ${cargoTomlPath}...`);
  try {
    execSync(`cd "${dir}" && cargo cyclonedx --override-filename "sbom-temp" --format json`, {
      stdio: 'inherit'
    });
    // Find the generated file
    const generatedFile = path.join(dir, 'sbom-temp.json');
    if (fs.existsSync(generatedFile)) {
      fs.renameSync(generatedFile, sbomFile);
      sbomFiles.push(sbomFile);
      console.log(`  ✓ Generated: ${sbomFile}\n`);
    }
  } catch (error) {
    console.log(`  ⚠ Warning: Failed to generate SBOM for ${cargoTomlPath}\n`);
  }
}

// Generate Python SBOMs
for (let i = 0; i < pythonProjectDirs.length; i++) {
  const pythonProject = pythonProjectDirs[i];
  const dir = pythonProject.dir;
  const sbomFile = path.join(tempDir, `sbom-python-${i}.json`);
  
  console.log(`🐍 Generating SBOM for ${dir}...`);
  try {
    // Only support pyproject.toml (PEP 621) - use temporary virtual environment to get proper dependency graph
    // This ensures we only scan declared dependencies with proper relationships
    const tempVenv = path.join(tempDir, `venv-${i}`);
    let command = '';
    
    try {
      // Create temporary virtual environment
      console.log(`  Creating temporary virtual environment...`);
      execSync(`python3 -m venv "${tempVenv}"`, {
        stdio: 'pipe'
      });
      
      // Get the Python executable in the venv
      const venvPython = process.platform === 'win32' 
        ? path.join(tempVenv, 'Scripts', 'python.exe')
        : path.join(tempVenv, 'bin', 'python');
      
      // Install the project in the venv (this will install only declared deps and their transitive deps)
      console.log(`  Installing project in virtual environment...`);
      execSync(`"${venvPython}" -m pip install --quiet --upgrade pip`, {
        stdio: 'pipe'
      });
      // Install cyclonedx-py in the venv so we can use it
      execSync(`"${venvPython}" -m pip install --quiet cyclonedx-bom`, {
        stdio: 'pipe'
      });
      execSync(`cd "${dir}" && "${venvPython}" -m pip install --quiet -e .`, {
        stdio: 'pipe'
      });
      
      // Use cyclonedx-py environment from the venv - this will build the dependency graph
      // The --pyproject flag helps identify the root component
      command = `cd "${dir}" && "${venvPython}" -m cyclonedx_py environment --pyproject "${pythonProject.pyprojectToml}" -o "${sbomFile}"`;
    } catch (venvError) {
      console.error(`  ❌ Error: Could not create virtual environment: ${venvError.message}`);
      throw new Error(`Failed to create virtual environment for ${dir}: ${venvError.message}`);
    }
    
    // Ensure command is set before executing
    if (!command) {
      console.log(`  ⚠ Warning: No command generated for ${dir}, skipping.`);
      continue;
    }
    
    execSync(command, {
      stdio: 'inherit'
    });
    
    if (fs.existsSync(sbomFile)) {
      sbomFiles.push(sbomFile);
      console.log(`  ✓ Generated: ${sbomFile}\n`);
    }
  } catch (error) {
    console.log(`  ⚠ Warning: Failed to generate SBOM for ${dir}\n`);
  }
}

if (sbomFiles.length === 0) {
  console.error('❌ No SBOM files were generated. Exiting.');
  process.exit(1);
}

console.log(`\n🔗 Merging ${sbomFiles.length} SBOM file(s)...\n`);

// Merge all SBOMs
const componentMap = new Map();
const dependencyMap = new Map();
let mergedMetadata = null;

for (const sbomFile of sbomFiles) {
  try {
    const sbom = JSON.parse(fs.readFileSync(sbomFile, 'utf8'));
    
    // Use first SBOM's metadata as base
    if (!mergedMetadata) {
      mergedMetadata = sbom.metadata;
    }
    
    // Merge components
    (sbom.components || []).forEach(comp => {
      const key = comp.purl || `${comp.group || ''}/${comp.name}@${comp.version}`;
      if (!componentMap.has(key)) {
        componentMap.set(key, comp);
      }
    });
    
    // Merge dependencies
    (sbom.dependencies || []).forEach(dep => {
      const key = dep.ref;
      if (!dependencyMap.has(key)) {
        dependencyMap.set(key, dep);
      } else {
        // Merge dependsOn arrays
        const existing = dependencyMap.get(key);
        const existingDeps = new Set(existing.dependsOn || []);
        (dep.dependsOn || []).forEach(d => existingDeps.add(d));
        existing.dependsOn = Array.from(existingDeps);
      }
    });
  } catch (error) {
    console.error(`  ⚠ Error reading ${sbomFile}: ${error.message}`);
  }
}

// Create merged SBOM
const mergedSbom = {
  $schema: "http://cyclonedx.org/schema/bom-1.6.schema.json",
  bomFormat: "CycloneDX",
  specVersion: "1.6",
  version: 1,
  serialNumber: `urn:uuid:${crypto.randomUUID()}`,
  metadata: {
    ...mergedMetadata,
    component: {
      type: "application",
      name: path.basename(process.cwd()),
      version: "1.0.0",
      bomRef: `${path.basename(process.cwd())}@1.0.0`
    },
    timestamp: new Date().toISOString()
  },
  components: Array.from(componentMap.values()),
  dependencies: Array.from(dependencyMap.values())
};

const outputFile = 'sbom.cyclonedx.json';
fs.writeFileSync(outputFile, JSON.stringify(mergedSbom, null, 2));
console.log(`✓ Merged SBOM created: ${outputFile}\n`);

// Clean up temp files and virtual environments
sbomFiles.forEach(f => {
  if (fs.existsSync(f)) fs.unlinkSync(f);
});
if (fs.existsSync(tempDir)) {
  // Remove directory recursively (Node.js 14.14.0+)
  // This will also remove any temporary virtual environments
  try {
    if (fs.rmSync) {
      fs.rmSync(tempDir, { recursive: true, force: true });
    } else {
      // Fallback for older Node.js versions
      const tempFiles = fs.readdirSync(tempDir);
      tempFiles.forEach(file => {
        const filePath = path.join(tempDir, file);
        if (fs.statSync(filePath).isFile()) {
          fs.unlinkSync(filePath);
        } else {
          // Handle directories (including venv directories)
          fs.rmdirSync(filePath, { recursive: true });
        }
      });
      fs.rmdirSync(tempDir);
    }
  } catch (e) {
    // Ignore cleanup errors
  }
}

// Analyze licenses
console.log('📋 License Analysis\n');
console.log('='.repeat(60));

// Helper function to check if an expression is just a single license ID (no operators)
const isSingleLicenseId = (expression) => {
  if (!expression || typeof expression !== 'string') {
    return false;
  }
  // Remove whitespace and check if it contains operators
  const trimmed = expression.trim();
  // Check for common SPDX operators (case-insensitive)
  if (/\s+(?:AND|OR|WITH|\+)\s+/i.test(trimmed)) {
    return false;
  }
  // Check for parentheses (indicates complex expression)
  if (trimmed.includes('(') || trimmed.includes(')')) {
    return false;
  }
  // If no operators or parentheses, it's likely a single license ID
  return trimmed.length > 0;
};

// Helper function to check if expression contains AND or WITH (not just OR)
// AND/WITH mean both licenses apply, so we should extract them
const hasAndOrWith = (expression) => {
  if (!expression || typeof expression !== 'string') {
    return false;
  }
  // Check for AND or WITH operators (case-insensitive)
  return /\s+(?:AND|WITH)\s+/i.test(expression);
};

// Helper function to check if a license ID is known (in the set or configured)
const isKnownLicense = (licenseId, knownLicenseSet) => {
  if (!licenseId) return false;
  const normalized = licenseId.toLowerCase();
  // Check if it's in the known set
  for (const known of knownLicenseSet) {
    if (known.toLowerCase() === normalized) return true;
  }
  // Check if it's in configured licenses (case-insensitive)
  const allConfigured = [...allowLicenses, ...reviewRequiredLicenses, ...counselRequiredLicenses];
  return allConfigured.some(lic => lic.toLowerCase() === normalized);
};

// Helper function to extract license IDs from expressions
// Only extracts when expression contains AND or WITH (not just OR)
// Exception: Don't extract exceptions from WITH clauses if they're part of an OR expression
// AND only ignore exceptions if the alternative license is already known
const extractLicenseIdsFromExpression = (expression, knownLicenseSet = new Set()) => {
  const licenseIds = new Set();
  
  if (!expression || typeof expression !== 'string') {
    return licenseIds;
  }
  
  // Only extract if expression contains AND or WITH
  if (!hasAndOrWith(expression)) {
    return licenseIds; // Don't extract from OR-only expressions
  }
  
  // Check if expression contains OR (case-insensitive)
  const hasOr = /\s+OR\s+/i.test(expression);
  
  // If expression contains OR, we need to be more careful with WITH clauses
  // WITH clauses that are part of OR expressions should be ignored only if there's a known alternative
  if (hasOr && /\s+WITH\s+/i.test(expression)) {
    // Parse the expression more carefully
    // Split by OR first to see if WITH is in an OR branch
    const orParts = expression.split(/\s+OR\s+/i);
    
    // Collect all alternative licenses (from parts without WITH)
    const alternatives = [];
    orParts.forEach(orPart => {
      const trimmedPart = orPart.trim().replace(/^\(+|\)+$/g, '').trim();
      if (!/\s+WITH\s+/i.test(trimmedPart)) {
        // This is an alternative without WITH - extract licenses from it
        const andParts = trimmedPart.split(/\s+AND\s+/i);
        andParts.forEach(andPart => {
          const cleaned = andPart.trim().replace(/^\(+|\)+$/g, '').trim().replace(/\++$/, '');
          if (cleaned && !/^(AND|OR|WITH|\+)$/i.test(cleaned)) {
            alternatives.push(cleaned);
          }
        });
      }
    });
    
    // Check if any alternative is already known
    const hasKnownAlternative = alternatives.some(alt => isKnownLicense(alt, knownLicenseSet));
    
    // Check each OR part
    orParts.forEach(orPart => {
      const trimmedPart = orPart.trim().replace(/^\(+|\)+$/g, '').trim();
      
      // If this OR part contains WITH, skip extracting the exception part
      // BUT only if there's a known alternative
      if (/\s+WITH\s+/i.test(trimmedPart)) {
        // Extract the main license (before WITH), but not the exception
        const withMatch = trimmedPart.match(/^(.+?)\s+WITH\s+/i);
        if (withMatch) {
          const mainLicense = withMatch[1].trim().replace(/^\(+|\)+$/g, '').trim();
          if (mainLicense && !/^(AND|OR|WITH|\+)$/i.test(mainLicense)) {
            const cleaned = mainLicense.replace(/\++$/, '');
            if (cleaned) licenseIds.add(cleaned);
          }
        }
        // Only skip the exception if there's a known alternative
        if (!hasKnownAlternative) {
          // No known alternative, so we need to extract the exception too
          const exceptionMatch = trimmedPart.match(/\s+WITH\s+(.+)$/i);
          if (exceptionMatch) {
            const exception = exceptionMatch[1].trim().replace(/^\(+|\)+$/g, '').trim();
            if (exception && !/^(AND|OR|WITH|\+)$/i.test(exception)) {
              const cleaned = exception.replace(/\++$/, '');
              if (cleaned) licenseIds.add(cleaned);
            }
          }
        }
      } else {
        // This OR part doesn't have WITH, so extract all licenses from it
        // Split by AND to get individual licenses
        const andParts = trimmedPart.split(/\s+AND\s+/i);
        andParts.forEach(andPart => {
          const cleaned = andPart.trim().replace(/^\(+|\)+$/g, '').trim().replace(/\++$/, '');
          if (cleaned && !/^(AND|OR|WITH|\+)$/i.test(cleaned)) {
            licenseIds.add(cleaned);
          }
        });
      }
    });
    
    return licenseIds;
  }
  
  // No OR in expression, or no WITH - extract normally
  // Remove parentheses and normalize whitespace
  let normalized = expression.replace(/[()]/g, ' ').replace(/\s+/g, ' ').trim();
  
  // Split by all operators (AND, OR, WITH, +) to get individual parts
  const parts = normalized.split(/\s+(?:AND|OR|WITH|\+)\s+/i);
  
  parts.forEach(part => {
    // Clean up the part (remove any remaining operators, trim)
    part = part.trim().replace(/^\(+|\)+$/g, '').trim();
    
    // Skip if empty or if it's just an operator
    if (!part || /^(AND|OR|WITH|\+)$/i.test(part)) {
      return;
    }
    
    // Handle version suffixes like "MIT+" or "GPL-2.0+"
    part = part.replace(/\++$/, '');
    
    // Add the license ID
    if (part) {
      licenseIds.add(part);
    }
  });
  
  return licenseIds;
};

const licenseIds = new Set();
const licenseExpressions = new Set();
const licenseNames = new Set();
const componentsWithoutLicense = [];
const componentsWithStrangeLicenses = [];
const componentsWithUnknownLicense = [];
const licenseCounts = new Map();

// Build component map by bom-ref for dependency lookup
const componentByBomRef = new Map();
mergedSbom.components.forEach(comp => {
  if (comp['bom-ref']) {
    componentByBomRef.set(comp['bom-ref'], comp);
  }
});

// Build reverse dependency map (what depends on what)
const reverseDeps = new Map();
mergedSbom.dependencies.forEach(dep => {
  if (dep.dependsOn) {
    dep.dependsOn.forEach(depRef => {
      if (!reverseDeps.has(depRef)) {
        reverseDeps.set(depRef, []);
      }
      reverseDeps.get(depRef).push(dep.ref);
    });
  }
});

mergedSbom.components.forEach(comp => {
  const compName = `${comp.group ? comp.group + '/' : ''}${comp.name}@${comp.version}`;
  let compType = 'Unknown';
  if (comp.purl) {
    if (comp.purl.startsWith('pkg:cargo')) {
      compType = 'Rust';
    } else if (comp.purl.startsWith('pkg:pypi')) {
      compType = 'Python';
    } else if (comp.purl.startsWith('pkg:npm')) {
      compType = 'NPM';
    }
  } else {
    // Fallback detection for components without purl
    // Check bom-ref format: Python packages often use "name==version" format
    const bomRefCheck = comp['bom-ref'] || '';
    if (bomRefCheck.includes('==') && !bomRefCheck.includes('@')) {
      compType = 'Python';
    } else if (comp.externalReferences) {
      // Check external references for Python-related paths
      const hasPythonPath = comp.externalReferences.some(ref => 
        ref.url && (ref.url.includes('/python/') || ref.url.includes('pypi') || ref.comment === 'PackageSource: Local')
      );
      if (hasPythonPath) {
        compType = 'Python';
      }
    }
  }
  const bomRef = comp['bom-ref'] || `${compName}`;
  
  if (comp.licenses && comp.licenses.length > 0) {
    let hasUnknown = false;
    comp.licenses.forEach(license => {
      if (license.license) {
        if (license.license.id) {
          licenseIds.add(license.license.id);
          licenseCounts.set(license.license.id, (licenseCounts.get(license.license.id) || 0) + 1);
        }
        if (license.license.expression) {
          licenseExpressions.add(license.license.expression);
          // If expression is just a single license ID, also add it to licenseIds
          if (isSingleLicenseId(license.license.expression)) {
            const singleId = license.license.expression.trim();
            licenseIds.add(singleId);
            licenseCounts.set(singleId, (licenseCounts.get(singleId) || 0) + 1);
          } else if (hasAndOrWith(license.license.expression)) {
            // Expression contains AND or WITH - extract all license IDs
            // Pass current licenseIds set to check if alternatives are known
            const extractedIds = extractLicenseIdsFromExpression(license.license.expression, licenseIds);
            extractedIds.forEach(id => {
              licenseIds.add(id);
              licenseCounts.set(id, (licenseCounts.get(id) || 0) + 1);
            });
            // Still mark as strange license for reporting
            componentsWithStrangeLicenses.push({
              name: compName,
              type: compType,
              bomRef: bomRef,
              expression: license.license.expression
            });
          } else {
            // OR-only expression - mark as strange license but don't extract
            componentsWithStrangeLicenses.push({
              name: compName,
              type: compType,
              bomRef: bomRef,
              expression: license.license.expression
            });
          }
        }
        if (license.license.name && !license.license.id) {
          licenseNames.add(license.license.name);
          if (license.license.name === 'Unknown') {
            hasUnknown = true;
            componentsWithUnknownLicense.push({
              name: compName,
              type: compType,
              bomRef: bomRef,
              nameOnly: license.license.name
            });
          } else {
            componentsWithStrangeLicenses.push({
              name: compName,
              type: compType,
              bomRef: bomRef,
              nameOnly: license.license.name
            });
          }
        }
      } else if (license.expression) {
        // Handle direct expression (without nested license object)
        licenseExpressions.add(license.expression);
        // If expression is just a single license ID, also add it to licenseIds
        if (isSingleLicenseId(license.expression)) {
          const singleId = license.expression.trim();
          licenseIds.add(singleId);
          licenseCounts.set(singleId, (licenseCounts.get(singleId) || 0) + 1);
        } else if (hasAndOrWith(license.expression)) {
          // Expression contains AND or WITH - extract all license IDs
          // Pass current licenseIds set to check if alternatives are known
          const extractedIds = extractLicenseIdsFromExpression(license.expression, licenseIds);
          extractedIds.forEach(id => {
            licenseIds.add(id);
            licenseCounts.set(id, (licenseCounts.get(id) || 0) + 1);
          });
          // Still mark as strange license for reporting
          componentsWithStrangeLicenses.push({
            name: compName,
            type: compType,
            bomRef: bomRef,
            expression: license.expression
          });
        } else {
          // OR-only expression - mark as strange license but don't extract
          componentsWithStrangeLicenses.push({
            name: compName,
            type: compType,
            bomRef: bomRef,
            expression: license.expression
          });
        }
      } else if (license.name) {
        licenseNames.add(license.name);
        if (license.name === 'Unknown') {
          hasUnknown = true;
          componentsWithUnknownLicense.push({
            name: compName,
            type: compType,
            bomRef: bomRef,
            nameOnly: license.name
          });
        } else {
          componentsWithStrangeLicenses.push({
            name: compName,
            type: compType,
            bomRef: bomRef,
            nameOnly: license.name
          });
        }
      }
    });
  } else {
    componentsWithoutLicense.push({
      name: compName,
      type: compType,
      bomRef: bomRef,
      purl: comp.purl
    });
  }
});

// Print results
console.log(`\n📊 Summary:`);
console.log(`  Total components: ${mergedSbom.components.length}`);
console.log(`  Total dependencies: ${mergedSbom.dependencies.length}`);
console.log(`  Components with licenses: ${mergedSbom.components.length - componentsWithoutLicense.length}`);
console.log(`  Components without licenses: ${componentsWithoutLicense.length}`);
console.log(`  Components with Unknown licenses: ${componentsWithUnknownLicense.length}`);
console.log(`  Components requiring legal counsel: ${componentsWithoutLicense.length + componentsWithUnknownLicense.length}`);

console.log(`\n📜 License Types (${licenseIds.size} unique):`);
const sortedLicenses = Array.from(licenseIds).sort();
console.log(`  ${sortedLicenses.join(', ')}`);

// Helper function to check if license matches (handles variations)
const matchesLicense = (license, list) => {
  return list.some(allowed => {
    // Exact match (case-sensitive)
    if (license === allowed) return true;
    
    // Case-insensitive exact match
    if (license.toLowerCase() === allowed.toLowerCase()) return true;
    
    // Handle "or-later" and "or-only" variations
    const baseLicense = allowed.split('-')[0]; // Get base like "GPL", "LGPL", "AGPL"
    // Case-insensitive prefix match
    if (license.toLowerCase().startsWith(baseLicense.toLowerCase())) {
      // Check for version match
      const allowedVersion = allowed.match(/\d+\.\d+/)?.[0];
      const licenseVersion = license.match(/\d+\.\d+/)?.[0];
      if (allowedVersion && licenseVersion && allowedVersion === licenseVersion) {
        return true;
      }
      // Handle "or-later" and "only" suffixes
      if (license.includes('-or-later') || license.includes('-only')) {
        return true;
      }
    }
    
    // Handle BSD variations (BSD-2-Clause, BSD-3-Clause, etc.)
    if (allowed.toLowerCase().startsWith('bsd-') && license.toLowerCase().startsWith('bsd-')) {
      const allowedNum = allowed.match(/\d+/)?.[0];
      const licenseNum = license.match(/\d+/)?.[0];
      if (allowedNum && licenseNum && allowedNum === licenseNum) return true;
    }
    
    // Handle LGPL variations
    if (allowed.toLowerCase().startsWith('lgpl-') && license.toLowerCase().startsWith('lgpl-')) {
      const allowedVersion = allowed.match(/\d+\.\d+/)?.[0];
      const licenseVersion = license.match(/\d+\.\d+/)?.[0];
      if (allowedVersion && licenseVersion && allowedVersion === licenseVersion) return true;
      if (license.includes('-or-later')) return true;
    }
    
    // Handle GPL variations
    if (allowed.toLowerCase().startsWith('gpl-') && license.toLowerCase().startsWith('gpl-')) {
      const allowedVersion = allowed.match(/\d+\.\d+/)?.[0];
      const licenseVersion = license.match(/\d+\.\d+/)?.[0];
      if (allowedVersion && licenseVersion && allowedVersion === licenseVersion) return true;
      if (license.includes('-or-later') || license.includes('-only')) return true;
    }
    
    // Handle AGPL variations
    if (allowed.toLowerCase().startsWith('agpl-') && license.toLowerCase().startsWith('agpl-')) {
      const allowedVersion = allowed.match(/\d+\.\d+/)?.[0];
      const licenseVersion = license.match(/\d+\.\d+/)?.[0];
      if (allowedVersion && licenseVersion && allowedVersion === licenseVersion) return true;
      if (license.includes('-or-later') || license.includes('-only')) return true;
    }
    
    return false;
  });
};

// Categorize found licenses
const allowFound = [];
const reviewFound = [];
const counselFound = [];
const uncategorized = [];

Array.from(licenseIds).forEach(license => {
  if (matchesLicense(license, allowLicenses)) {
    allowFound.push(license);
  } else if (matchesLicense(license, reviewRequiredLicenses)) {
    reviewFound.push(license);
  } else if (matchesLicense(license, counselRequiredLicenses)) {
    counselFound.push(license);
  } else {
    uncategorized.push(license);
  }
});

// Print categorization
console.log(`\n🔐 License Categorization:`);
console.log(`\n✅ ALLOW (No approval required) - ${allowFound.length} license(s):`);
if (allowFound.length > 0) {
  allowFound.sort().forEach(license => {
    const count = licenseCounts.get(license) || 0;
    console.log(`  - ${license} (${count} component(s))`);
  });
} else {
  console.log(`  (none)`);
}

console.log(`\n⚠️  REVIEW REQUIRED - ${reviewFound.length} license(s):`);
if (reviewFound.length > 0) {
  reviewFound.sort().forEach(license => {
    const count = licenseCounts.get(license) || 0;
    console.log(`  - ${license} (${count} component(s))`);
  });
} else {
  console.log(`  (none)`);
}

// Collect all problematic components requiring counsel
const counselRequiredComponents = [];
const counselComponentDeps = new Map();

// Add components with Unknown licenses
componentsWithUnknownLicense.forEach(comp => {
  counselRequiredComponents.push({
    name: comp.name,
    type: comp.type,
    reason: 'Unknown license',
    bomRef: comp.bomRef
  });
  const deps = reverseDeps.get(comp.bomRef) || [];
  counselComponentDeps.set(comp.bomRef, deps);
});

// Add components without licenses
componentsWithoutLicense.forEach(comp => {
  counselRequiredComponents.push({
    name: comp.name,
    type: comp.type,
    reason: 'No license',
    bomRef: comp.bomRef
  });
  const deps = reverseDeps.get(comp.bomRef) || [];
  counselComponentDeps.set(comp.bomRef, deps);
});

console.log(`\n🚨 MUST OBTAIN COUNSEL + COMPLIANCE PLAN - ${counselFound.length} license type(s) + ${counselRequiredComponents.length} problematic component(s):`);
if (counselFound.length > 0) {
  counselFound.sort().forEach(license => {
    const count = licenseCounts.get(license) || 0;
    console.log(`  - ${license} (${count} component(s))`);
  });
}

if (counselRequiredComponents.length > 0) {
  // Group components by reason type
  const componentsByReason = new Map();
  counselRequiredComponents.forEach(comp => {
    if (!componentsByReason.has(comp.reason)) {
      componentsByReason.set(comp.reason, []);
    }
    componentsByReason.get(comp.reason).push(comp);
  });
  
  // Print each reason type with its components
  componentsByReason.forEach((components, reason) => {
    console.log(`\n  ${reason} (${components.length} component(s)):`);
    components.forEach(comp => {
      console.log(`    - ${comp.name} (${comp.type})`);
      const deps = counselComponentDeps.get(comp.bomRef) || [];
      if (deps.length > 0) {
        console.log(`      Dependencies (${deps.length} component(s) depend on this):`);
        deps.slice(0, 10).forEach(depRef => {
          const depComp = componentByBomRef.get(depRef);
          if (depComp) {
            const depName = `${depComp.group ? depComp.group + '/' : ''}${depComp.name}@${depComp.version}`;
            console.log(`        • ${depName}`);
          } else {
            console.log(`        • ${depRef}`);
          }
        });
        if (deps.length > 10) {
          console.log(`        ... and ${deps.length - 10} more`);
        }
      } else {
        console.log(`      (No dependencies found - may be a direct dependency)`);
      }
    });
  });
}

if (counselFound.length === 0 && counselRequiredComponents.length === 0) {
  console.log(`  (none)`);
}

console.log(`\n❓ UNCATEGORIZED (Not in any category) - ${uncategorized.length} license(s):`);
if (uncategorized.length > 0) {
  uncategorized.sort().forEach(license => {
    const count = licenseCounts.get(license) || 0;
    console.log(`  - ${license} (${count} component(s))`);
  });
} else {
  console.log(`  (none)`);
}

if (componentsWithStrangeLicenses.length > 0) {
  console.log(`\n🔍 Components with Unusual License Formats (${componentsWithStrangeLicenses.length}):`);
  componentsWithStrangeLicenses.slice(0, 10).forEach(c => {
    if (c.expression) {
      console.log(`  - ${c.name} (${c.type}): expression="${c.expression}"`);
    } else if (c.nameOnly) {
      console.log(`  - ${c.name} (${c.type}): name="${c.nameOnly}" (no ID)`);
    }
  });
  if (componentsWithStrangeLicenses.length > 10) {
    console.log(`  ... and ${componentsWithStrangeLicenses.length - 10} more`);
  }
}

if (licenseExpressions.size > 0) {
  console.log(`\n📝 License Expressions Found (${licenseExpressions.size}):`);
  Array.from(licenseExpressions).forEach(expr => {
    console.log(`  - ${expr}`);
  });
}

if (licenseNames.size > 0) {
  console.log(`\n📝 License Names (without IDs) Found (${licenseNames.size}):`);
  Array.from(licenseNames).forEach(name => {
    console.log(`  - ${name}`);
  });
}

console.log(`\n${'='.repeat(60)}`);

// Generate new-LICENSE-THIRD-PARTY.txt
console.log(`\n📄 Generating new-LICENSE-THIRD-PARTY.txt...`);
const configuredLicenseIdList = LICENSES_TO_INCLUDE.map(l => l.id || l).join(', ');
console.log(`  Including ${LICENSES_TO_INCLUDE.length} specified license(s): ${configuredLicenseIdList}`);

// Collect all licenses found in SBOM
// Collect explicit license IDs, single-license expressions, and licenses from AND/WITH expressions
const allLicensesInSBOM = new Set();
mergedSbom.components.forEach(comp => {
  if (comp.licenses) {
    comp.licenses.forEach(license => {
      if (license.license) {
        // Collect explicit license IDs
        if (license.license.id) {
          allLicensesInSBOM.add(license.license.id);
        }
        // Collect single-license expressions (treat them as license IDs)
        if (license.license.expression && isSingleLicenseId(license.license.expression)) {
          allLicensesInSBOM.add(license.license.expression.trim());
        }
        // Collect license IDs from expressions containing AND or WITH
        // Pass current allLicensesInSBOM set to check if alternatives are known
        if (license.license.expression && hasAndOrWith(license.license.expression)) {
          const extractedIds = extractLicenseIdsFromExpression(license.license.expression, allLicensesInSBOM);
          extractedIds.forEach(id => allLicensesInSBOM.add(id));
        }
      } else if (license.expression) {
        // Collect single-license expressions (treat them as license IDs)
        if (isSingleLicenseId(license.expression)) {
          allLicensesInSBOM.add(license.expression.trim());
        }
        // Collect license IDs from expressions containing AND or WITH
        // Pass current allLicensesInSBOM set to check if alternatives are known
        if (hasAndOrWith(license.expression)) {
          const extractedIds = extractLicenseIdsFromExpression(license.expression, allLicensesInSBOM);
          extractedIds.forEach(id => allLicensesInSBOM.add(id));
        }
      }
    });
  }
});

// Helper function to normalize a license ID using the LICENSE_VARIATIONS map (for text lookup only)
// Also handles case-insensitive matching
const normalizeLicenseId = (licenseId) => {
  // First check exact match (case-sensitive)
  if (LICENSE_VARIATIONS[licenseId]) {
    return LICENSE_VARIATIONS[licenseId];
  }
  
  // Then check case-insensitive match
  const lowerLicenseId = licenseId.toLowerCase();
  for (const [variation, base] of Object.entries(LICENSE_VARIATIONS)) {
    if (variation.toLowerCase() === lowerLicenseId) {
      return base;
    }
  }
  
  return licenseId;
};

// Helper function to format display name from license ID (e.g., "LGPL-3.0-or-later" -> "LGPL 3.0 or later")
const formatDisplayName = (licenseId) => {
  // Replace hyphens with spaces, but preserve version numbers
  return licenseId
    .replace(/-or-later/g, ' or later')
    .replace(/-only/g, ' only')
    .replace(/-/g, ' ')
    .replace(/(\d)\s+(\d)/g, '$1.$2') // Fix version numbers like "3 0" -> "3.0"
    .replace(/\s+/g, ' ')
    .trim();
};

// Helper function to check if a license from SBOM matches any configured license
const matchesConfiguredLicense = (sbomLicenseId) => {
  const normalizedId = normalizeLicenseId(sbomLicenseId);
  // Case-insensitive comparison
  const normalizedLower = normalizedId.toLowerCase();
  return LICENSES_TO_INCLUDE.some(licenseConfig => 
    licenseConfig.id.toLowerCase() === normalizedLower
  );
};

// Collect licenses found in SBOM - include each variation separately, but use base license text
const licensesToInclude = new Map();
const licenseTextsFromSBOM = new Map();
const configuredLicenseIds = new Set();

// Build set of configured license IDs for quick lookup
LICENSES_TO_INCLUDE.forEach(licenseConfig => {
  configuredLicenseIds.add(licenseConfig.id);
});

  // For each license found in SBOM, create an entry
Array.from(allLicensesInSBOM).forEach(sbomLicenseId => {
  const normalizedId = normalizeLicenseId(sbomLicenseId);
  
  // Check if this license (or its variation) matches a configured license (case-insensitive)
  const normalizedLower = normalizedId.toLowerCase();
  if (LICENSES_TO_INCLUDE.some(licenseConfig => licenseConfig.id.toLowerCase() === normalizedLower)) {
    // Find the base license config to get the text (case-insensitive)
    const baseLicenseConfig = LICENSES_TO_INCLUDE.find(l => l.id.toLowerCase() === normalizedLower);
    
    if (baseLicenseConfig) {
      // Include this specific variation with its own display name
      licensesToInclude.set(sbomLicenseId, {
        id: sbomLicenseId,
        displayName: formatDisplayName(sbomLicenseId),
        baseLicenseId: normalizedId, // Store the base ID for text lookup
        text: baseLicenseConfig.text || null
      });
      
      // Store the license text keyed by the base license ID
      if (baseLicenseConfig.text) {
        licenseTextsFromSBOM.set(normalizedId, baseLicenseConfig.text);
      }
    }
  }
});

// Find licenses in SBOM that are not matched by any configured license
const missingLicenses = Array.from(allLicensesInSBOM).filter(licenseId => !matchesConfiguredLicense(licenseId));

// Find licenses in configuration that are not in the SBOM (for informational purposes)
const unusedConfiguredLicenses = LICENSES_TO_INCLUDE
  .map(l => l.id)
  .filter(licenseId => !allLicensesInSBOM.has(licenseId));

// Generate file (no need to fetch since texts are provided in config)
(async () => {
  // Normalize line terminators for provided license texts
  licenseTextsFromSBOM.forEach((text, licenseId) => {
    const normalizedText = text
      .replace(/\u2028/g, '\n')  // Line Separator (LS)
      .replace(/\u2029/g, '\n')  // Paragraph Separator (PS)
      .replace(/\r\n/g, '\n')    // Windows CRLF
      .replace(/\r/g, '\n')      // Old Mac CR
      .replace(/\n{3,}/g, '\n\n'); // Normalize multiple newlines to max 2
    licenseTextsFromSBOM.set(licenseId, normalizedText);
  });

  // Build the license file content
  let licenseFileContent = `========================================================================
LICENSE-THIRD-PARTY.txt
========================================================================

This file includes the full text of open-source licenses that apply to certain third-party components used or distributed with this project. All respective copyrights are retained by their owners.

`;

  // Add warning about missing licenses if any
  if (missingLicenses.length > 0) {
    licenseFileContent += `========================================================================
⚠️  WARNING: MISSING LICENSES
========================================================================

The following licenses were found in the project dependencies but are NOT included in this file. Their full texts need to be added:

`;
    missingLicenses.sort().forEach(licenseId => {
      const count = Array.from(mergedSbom.components).filter(comp => 
        comp.licenses && comp.licenses.some(l => l.license && l.license.id === licenseId)
      ).length;
      licenseFileContent += `  - ${licenseId} - used by ${count} component(s)\n`;
    });
    licenseFileContent += `\nPlease add these licenses to the LICENSES_TO_INCLUDE configuration in generate-sbom.js with their full license texts.\n\n`;
  }

  // Sort licenses: group by base license, then by variation name
  // First, collect all unique base licenses that are found
  const baseLicensesFound = new Set();
  licensesToInclude.forEach((licenseInfo, licenseId) => {
    baseLicensesFound.add(licenseInfo.baseLicenseId || licenseId);
  });
  
  // Build sorted entries: for each base license in LICENSES_TO_INCLUDE order,
  // include all its variations found in SBOM
  const sortedLicenseEntries = [];
  LICENSES_TO_INCLUDE.forEach(licenseConfig => {
    if (baseLicensesFound.has(licenseConfig.id)) {
      // Find all variations of this base license
      const variations = Array.from(licensesToInclude.entries())
        .filter(([licenseId, licenseInfo]) => 
          (licenseInfo.baseLicenseId || licenseId) === licenseConfig.id
        )
        .sort((a, b) => a[0].localeCompare(b[0])); // Sort variations alphabetically
      
      sortedLicenseEntries.push(...variations);
    }
  });

  // Add each license
  sortedLicenseEntries.forEach(([licenseId, licenseInfo], index) => {
    const sectionNumber = index + 1;
    // Get text from the base license ID
    const baseLicenseId = licenseInfo.baseLicenseId || licenseId;
    let licenseText = licenseTextsFromSBOM.get(baseLicenseId);
    
    // If no text found, use a placeholder
    if (!licenseText) {
      licenseText = `This license applies to components using the ${licenseInfo.displayName}. For the full license text, please refer to the official license documentation.`;
    }
    
    licenseFileContent += `========================================================================
${sectionNumber}. ${licenseInfo.displayName}
========================================================================

${licenseText}

`;
  });

  licenseFileContent += `========================================================================
END OF LICENSE-THIRD-PARTY.txt
========================================================================
`;

  // Normalize line terminators in the entire file content
  licenseFileContent = licenseFileContent
    .replace(/\u2028/g, '\n')  // Line Separator (LS)
    .replace(/\u2029/g, '\n')  // Paragraph Separator (PS)
    .replace(/\r\n/g, '\n')    // Windows CRLF
    .replace(/\r/g, '\n');     // Old Mac CR

  // Delete existing file if it exists
  const licenseFileName = 'new-LICENSE-THIRD-PARTY.txt';
  if (fs.existsSync(licenseFileName)) {
    fs.unlinkSync(licenseFileName);
    console.log(`  Deleted existing ${licenseFileName}`);
  }

  // Write the file
  fs.writeFileSync(licenseFileName, licenseFileContent, { encoding: 'utf8' });
  console.log(`✓ Generated: ${licenseFileName}`);
  console.log(`  Included ${sortedLicenseEntries.length} license(s)\n`);

  // Report missing licenses
  if (missingLicenses.length > 0) {
    console.log(`⚠️  MISSING LICENSES: The following licenses were found in the SBOM but are NOT included in new-LICENSE-THIRD-PARTY.txt:`);
    console.log(`\n  You need to add these ${missingLicenses.length} license(s) to the LICENSES_TO_INCLUDE configuration:`);
    missingLicenses.sort().forEach(licenseId => {
      const count = Array.from(mergedSbom.components).filter(comp => 
        comp.licenses && comp.licenses.some(l => l.license && l.license.id === licenseId)
      ).length;
      console.log(`    - ${licenseId} - used by ${count} component(s)`);
    });
    console.log(`\n  Add them to the LICENSES_TO_INCLUDE array at the top of generate-sbom.js with their full license texts.\n`);
  } else {
    console.log(`✓ All licenses found in SBOM are included in new-LICENSE-THIRD-PARTY.txt\n`);
  }

  // Report unused configured licenses (in config but not in SBOM)
  if (unusedConfiguredLicenses.length > 0) {
    console.log(`ℹ️  UNUSED LICENSES: The following licenses are in your configuration but were NOT found in the SBOM:`);
    unusedConfiguredLicenses.forEach(licenseId => {
      const licenseConfig = LICENSES_TO_INCLUDE.find(l => l.id === licenseId);
      const displayName = licenseConfig ? licenseConfig.displayName : licenseId;
      console.log(`    - ${licenseId}${displayName !== licenseId ? ` (${displayName})` : ''}`);
    });
    console.log(`\n  These licenses were not included in new-LICENSE-THIRD-PARTY.txt since they're not used by any dependencies.\n`);
  }

  console.log(`\n✅ Complete! SBOM saved to: ${outputFile}\n`);
})();
