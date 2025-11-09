// Root build.gradle.kts for Advanced Kotlin Learning
// This allows building all sub-projects together

plugins {
    kotlin("jvm") version "1.9.20" apply false
}

allprojects {
    group = "com.learning.kotlin.advanced"
    version = "1.0.0-SNAPSHOT"

    repositories {
        mavenCentral()
    }
}

subprojects {
    apply(plugin = "org.jetbrains.kotlin.jvm")

    dependencies {
        // Common dependencies for all sub-projects
        "implementation"(kotlin("stdlib"))
        "implementation"(kotlin("reflect"))

        // Testing
        "testImplementation"(kotlin("test"))
        "testImplementation"("org.junit.jupiter:junit-jupiter:5.10.0")
        "testImplementation"("io.mockk:mockk:1.13.8")
    }

    tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
        kotlinOptions {
            jvmTarget = "17"
            freeCompilerArgs = listOf(
                "-Xjsr305=strict",
                "-Xcontext-receivers" // Enable experimental context receivers
            )
        }
    }

    tasks.withType<Test> {
        useJUnitPlatform()
    }
}
